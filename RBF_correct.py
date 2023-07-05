#!/usr/bin/env python
import os
import argparse
import logging
import numpy as np
from numpy.linalg import norm
from astropy.io import fits
from astropy.table import Table
from astropy.wcs import WCS
from astropy.coordinates import Longitude, SkyCoord
from astropy import units as u

def transform_rbf(p, q, v, alpha=1, reverse=False, close_cutoff=0.0):
    n = len(p)
    distance = norm(p - v, axis=1)
    distance = np.where(distance == close_cutoff, close_cutoff, distance)
    w = distance ** (-2 * alpha) # figure out the weights for the different sources
    d = q-p
    if reverse:
        sign = -1.
    else:
        sign = 1.
    return v - sign*np.sum(d*w[:, None], axis=0)/sum(w)

parser = argparse.ArgumentParser()
parser.add_argument('cattable', help='Input table containing ionospheric offsets')
parser.add_argument('infits', help='Input FITS image (for WCS)')
parser.add_argument('intable', help='Input table to correct')
parser.add_argument('outtable', help='Input table to correct')
parser.add_argument('--beam_cutoff', default=0.1, type=float, help="beam cutoff (default: %(default)s)")
parser.add_argument("--alpha", default=2.0, type=float, help="RBF alpha (default=%(default)s)")
parser.add_argument("--reverse", dest="reverse", action="store_true", help="Reverse correction (e.g. make astrometrically catalogue match distorted image)")
parser.add_argument('--ra', default='ra', help="Apparant RA column (default: %(default)s)")
parser.add_argument('--dec', default='dec', help="Apparant Dec column (default: %(default)s)")
parser.add_argument('--ra_corr', default='ra_corr', help="Corrected RA column to add(default: %(default)s)")
parser.add_argument('--dec_corr', default='dec_corr', help="Catalogued Dec column to add (default: %(default)s)")
parser.add_argument('--beam', default='pbcor_norm', help="beam column (default: %(default)s)")
parser.add_argument('--complex', default='complex', help="Boolean column denoting 'complex' sources (default: %(default)s)")
parser.add_argument('--outlier', default='outlier', help="Boolean column denoting 'outlier' sources (default: %(default)s)")
parser.add_argument('--out_format', default='votable', help="output format (default: %(default)s)")
parser.add_argument("--no_overwrite", dest='overwrite', action="store_false", help="don't overwrite an existing beam (overwrites by default)")
parser.add_argument('--outformat', default="votable", help="output format (default: %(default)s)")
parser.add_argument("-v", "--verbose", action="count", dest="verbose", default=0, help="-v info, -vv debug")

args = parser.parse_args()

if not args.overwrite and os.path.exists(args.outtable):
    raise IOError("outtable exists")

if args.verbose == 0:
    logging.basicConfig(format='%(asctime)s-%(levelname)s %(message)s', level=logging.WARNING)
elif args.verbose == 1:
    logging.basicConfig(format='%(asctime)s-%(levelname)s %(message)s', level=logging.INFO)
else:
    logging.basicConfig(format='%(asctime)s-%(levelname)s %(message)s', level=logging.DEBUG)

table = Table.read(args.cattable)
tabarray = table.as_array()

header = fits.open(args.infits)[0].header
wcs = WCS(header).celestial

in_table = Table.read(args.intable)
in_table_array = in_table.as_array()


# boolean flags
vlss_complex = tabarray[args.complex]
outlier = tabarray[args.outlier]
# classify by beam
h = tabarray[args.beam] > args.beam_cutoff
fit = ~vlss_complex & ~outlier & h
logging.info("%d/%d sources from input catalogue selected for fit", np.sum(fit), len(fit))

p = np.stack((tabarray['x'][fit], tabarray['y'][fit]), axis=-1)
q = np.stack((tabarray['x_cat'][fit], tabarray['y_cat'][fit]), axis=-1)

def fix_long(l):
    """
    wcs.pixel_to_world returns RA > 180 or < -180 sometimes, probably
    due to CRPIX being a long way outside the image
    """
    return np.where(l<0, l+360, l) % 360

radec_v = SkyCoord(in_table_array[args.ra]*u.deg, in_table_array[args.dec]*u.deg)
x_v, y_v = wcs.world_to_pixel(radec_v)
v = np.stack((x_v, y_v), axis=-1)

d = np.zeros(v.shape)
for i in range(len(d)):
    d[i] = transform_rbf(q, p, v[[i], :], args.alpha, args.reverse)
ra_roundtrip = np.array(wcs.pixel_to_world_values(v))[:, 0]
ra_errors = np.abs(fix_long(ra_roundtrip) - fix_long(in_table_array[args.ra])) > 1e-4
n_error = np.sum(ra_errors)
for i in list(np.where(ra_errors)[0]):
	#print(i)
	print(f"{i:04d}, {in_table_array[args.ra][i]:.6f}, {ra_roundtrip[i]:.6f}, {fix_long(ra_roundtrip[i]):.6f}, {(in_table_array[args.ra][i]-ra_roundtrip[i]):.6e} deg err, {3600*(in_table_array[args.ra][i]-ra_roundtrip[i]):.6e} arcsec error")
assert n_error == 0, f"Error: Attempt to fix astropy bug failed for {n_error}/{len(d)} sources!"

radec_corr = np.array(wcs.pixel_to_world_values(d))
in_table[args.ra_corr] = (fix_long(radec_corr[:, 0]))*u.deg
in_table[args.dec_corr] = (radec_corr[:, 1])*u.deg
in_table.write(args.outtable, format=args.out_format, overwrite=args.overwrite)
