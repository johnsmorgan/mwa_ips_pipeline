#!/usr/bin/env python
from optparse import OptionParser #NB zeus does not have argparse!
import numpy as np
from astropy.io import fits
from image_stack import ImageStack

parser = OptionParser(usage = "usage:" +
    """
    python apply_beam.py \
               hdf5_file_in.h5py fitsfile_in.fits [fitsfile_in.fits] fitsfile_out.fits [-fr]
    """)
parser.add_option("-f", "--freq", default=None, dest="freq", help="freq")
parser.add_option("-i", "--stokesi", default=None, dest="combine", help="combine XX and YY into stokes I")
parser.add_option("-r", "--reverse", action='store_true', dest="reverse", help="remove an already-applied primary beam correction")

opts, args = parser.parse_args()

hdf5_in = args[0]
hdus = fits.open(args[1])
if not opts.combine:
    fits_out = args[2]
    in_data = hdus[0].data
else:
    hdusy = fits.open(args[2])
    fits_out = args[3]
    in_data = hdus[0].data, hdusy[0].data

if opts.freq is not None:
    group = opts.freq
else:
    group = '/'

if opts.freq is not None:
    df = ImageStack(hdf5_in, freq=opts.freq)
else:
    df = ImageStack(hdf5_in)
beam = df.group['beam'][..., 0, 0] # last two dimensions are frequency and time
n_x, n_y = in_data.shape[-1], in_data.shape[-2]
assert n_x == beam.shape[-3] and n_y == beam.shape[-4], "beam and image xy dimensions do not match %s %s %s" % (str(beam.shape), n_x, n_y)

if not opts.reverse:
    if not opts.combine:
        out_data = in_data*np.average(1/beam, weights=beam**2, axis=0)**-1
    else:
        out_data = in_data/np.average(1/beam, weights=beam**2, axis=0)**-1
else:
    out_data = in_data/np.average(1/beam, weights=beam**2, axis=0)**-1
hdus[0].data = out_data.reshape((1, 1, data_y, data_x))
hdus.writeto(fits_out)
