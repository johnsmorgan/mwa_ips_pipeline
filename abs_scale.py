#!/usr/bin/env python

import os, sys
import logging
import numpy as np
from h5py import File
from astropy.io import votable
from optparse import OptionParser #NB zeus does not have argparse!

IN_DIR="/data/ips/dr3/continuum"
IN_DIR="."

PB_THRESH = 0.9
SNR_THRESH = 10

N_POL=2
POLS = ("XX", "YY")
N_WARN=10
N_FAIL=2

def get_scale(in_cat, snr_thresh, pb_thresh):
    cal = votable.parse_single_table(in_cat).to_table()
    max_pb = np.max(cal['pbcor'])
    good = (cal['snr'] > opts.snr_thresh) & (cal['pbcor'] > opts.pb_thresh*max_pb)
    good = (good & ~cal['Fp162'].mask)

    cat = cal[good]
    n = len(cat)
    #scale = np.average(cat['peak_flux']/cat['pbcor']/cat['Fp162'])**-1
    #frac_err = np.std((cat['peak_flux']/cat['pbcor']/cat['Fp162'])**-1)/scale
    scale = np.average(cat['peak_flux']/cat['pbcor']/cat['Fp162'])
    frac_err = np.std((cat['peak_flux']/cat['pbcor']/cat['Fp162']))/scale
    return scale, frac_err, n

if __name__ == '__main__':
    parser = OptionParser(usage="usage: obsid freq" +
                          """
                          read [obsid]_[freq]_[pol]_image_cal.vot (pols XX and YY) and calculate absolute primary beam scaling
                          from sources with pbcor higher than pbthresh and snr higher than snr_thresh

                          Unless dry-run is set, these corrections will be written into [obsid].hdf5

                          """)

    parser.add_option("--pb_thresh", default=PB_THRESH, dest="pb_thresh", type="float", help="threshold relative to maximum pbcor in input file (default %default)")
    parser.add_option("--snr_thresh", default=SNR_THRESH, dest="snr_thresh", type="float", help="signal to noise threshold (default %default)")
    parser.add_option("--n_warn", default=N_WARN, dest="n_warn", type="float", help="warn if solution is based on less than this number of sources (default %default)")
    parser.add_option("--n_fail", default=N_FAIL, dest="n_fail", type="float", help="warn if solution is based on less than this number of sources (default %default)")
    parser.add_option("-v", "--verbose", action="count", dest="verbose", default=0, help="-v info, -vv debug")
    parser.add_option("-n", "--dry-run", action="store_true", dest="dry_run", help="don't actually write beam, open imstack read only")
    parser.add_option("--no_overwrite", action="store_true", dest="no_overwrite", help="don't overwrite an existing beam (overwrites by default)")
    parser.add_option("--csv", action="store_true", dest="csv", help="write out solutions as csv line")
    parser.add_option("--pols", default=','.join(POLS), dest="pols", type="string", help="polarisations as comma separated list (default %default)")

    opts, args = parser.parse_args()
    if len(args) != 2:
        parser.error("incorrect number of arguments")

    obsid = args[0]
    freq  = args[1]

    pols = opts.pols.split(',')

    if opts.verbose == 1:
        logging.basicConfig(format='%(asctime)s-%(levelname)s %(message)s', level=logging.INFO)
    elif opts.verbose > 1:
        logging.basicConfig(format='%(asctime)s-%(levelname)s %(message)s', level=logging.DEBUG)

    scales, frac_errors, ns = np.zeros((len(pols),)), np.zeros((len(pols),)), np.zeros((len(pols),))
    for p, pol in enumerate(pols):
        in_file = os.path.join(IN_DIR, "{}_{}-{}-image_cal.vot".format(obsid, freq, pol))
        #in_file = os.path.join(IN_DIR, "{}_{}-{}_cal.vot".format(obsid, freq, pol))
        logging.debug("opening %s", in_file)
        scale, frac_error, n = get_scale(in_file, opts.snr_thresh, opts.pb_thresh)
        logging.debug("%s %s %s", scale, frac_error, n)
        scales[p], frac_errors[p], ns[p] = scale, frac_error, n

        if n < opts.n_fail:
            raise RuntimeError("Can't get reliable solution from %s: Only %d sources" % (in_file, n))
        if n < opts.n_warn:
            logging.warn("only %d sources!", n)

    if opts.csv:
        print(f"{obsid}", end='')
        for p in range(len(pols)):
            print(f",{scales[p]},{ns[p]},{frac_errors[p]}", end='')
        print()
    logging.info("scale: %s", scales)
    logging.info("n: %s", ns)
    logging.info("frac_err: %s", frac_errors)

    if not opts.dry_run:
        #open beam file
        logging.debug("opening image stack")
        with File("%s.hdf5" % obsid, 'r+') as imstack:
            group = imstack[freq]
            beam = group['beam']
            scale_shape = [N_POL] + [1]*(len(beam.shape)-1)
            if not 'SCALE' in beam.attrs.keys():
                beam.attrs.create('SCALE', scales.reshape(scale_shape))
                assert 'SCALEN' not in beam.attrs.keys() and 'SCALEF' not in beam.attrs.keys(), "incomplete beam attrs"
                beam.attrs.create('SCALEN', ns.reshape(scale_shape))
                beam.attrs.create('SCALEF', frac_errors.reshape(scale_shape))
            else:
                assert 'SCALEN' in beam.attrs.keys() and 'SCALEF' in beam.attrs.keys(), "incomplete beam attrs"
                if opts.no_overwrite:
                    raise RuntimeError("beam dataset already exists and no_overwrite set!")
                else:
                    beam.attrs['SCALE'] = scales.reshape(scale_shape)
                    beam.attrs['SCALEN'] = ns.reshape(scale_shape)
                    beam.attrs['SCALEF'] = frac_errors.reshape(scale_shape)
