"""
Generate a table containing sources suitable for an rubber-sheet IPS solution
"""
import sys
import os
import argparse
import logging
import numpy as np

from numpy.linalg import norm
from astropy.table import Table
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import Longitude, SkyCoord
from astropy import units as u

def get_outliers(p, d, outlier_offset, n=3):
    """
    get list of indices in p which have minimum distance from v
    """
    outlier = np.zeros(len(p), dtype=bool)
    for i in range(len(p)):
	    dist = norm((p - p[i]), axis=1) # figure out the distances for sources
	    nearby = np.argsort(dist)[1:n+1]
	    if np.min(norm(d[i] - d[nearby])) > outlier_offset:
		    outlier[i] = True
    return outlier

parser = argparse.ArgumentParser()
parser.add_argument('intable', help='Input table')
parser.add_argument('infits', help='Input FITS image (for WCS)')
parser.add_argument('outtable', help='Output table name')
parser.add_argument('--ra', default='ra', help="Apparant RA column (default: %(default)s)")
parser.add_argument('--dec', default='dec', help="Apparant Dec column (default: %(default)s)")
parser.add_argument('--ra_cat', default='ra_cat', help="Catalogued RA column (default: %(default)s)")
parser.add_argument('--dec_cat', default='dec_cat', help="Catalogued Dec column (default: %(default)s)")
parser.add_argument('--out_format', default='votable', help="output format (default: %(default)s)")
parser.add_argument("--no_overwrite", dest='overwrite', action="store_false", help="don't overwrite an existing beam (overwrites by default)")
parser.add_argument('--fit_col', default='err_ra', help="Column that is -1 if aegean didn't fully fit (default: %(default)s)")
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

header = fits.open(args.infits)[0].header

table = Table.read(args.intable)
tabarray = table.as_array()

# remove sources that are not fit (pixel resolution accuracy only)
no_fit = tabarray[args.fit_col] == -1.0
logging.info("%d/%d  with no aegean fit", np.sum(no_fit), len(tabarray))
tabarray = tabarray[~no_fit]
table = table[~no_fit]

n = len(tabarray)
assert np.all(np.isfinite(tabarray[args.ra])), "Invalid values found in ra column!"
assert np.all(np.isfinite(tabarray[args.dec])), "Invalid values found in dec column!"
assert np.all(np.isfinite(tabarray[args.ra_cat])), "Invalid values found in ra_cat column!"
assert np.all(np.isfinite(tabarray[args.dec_cat])), "Invalid values found in dec_cat column!"

radec_p = SkyCoord(tabarray[args.ra]*u.deg, tabarray[args.dec]*u.deg)
radec_q = SkyCoord(tabarray[args.ra_cat]*u.deg, tabarray[args.dec_cat]*u.deg)

wcs = WCS(header).celestial
x_p, y_p = wcs.world_to_pixel(radec_p)
x_q, y_q = wcs.world_to_pixel(radec_q)
assert np.all(np.isfinite(x_p)) and np.all(np.isfinite(y_p)) and np.all(np.isfinite(x_q)) and np.all(np.isfinite(x_q)), "Invalid values found in x, y coordinates!"

# make a list of sources to exclude as outliers
p = np.stack((x_p, y_p), axis=-1)
d = np.stack((x_q, y_q), axis=-1) - p

outlier = get_outliers(p, d, 1.0/(60.0*abs(header['CDELT1']))) # outlier if 1arcmin offset at zenith
logging.info("%d/%d outliers", np.sum(outlier), len(p))

table['x'] = x_p
table['y'] = y_p
table['x_cat'] = x_q
table['y_cat'] = y_q
table['outlier'] = outlier
table.remove_columns(['peak_flux', 'local_rms', 'pbcor', 'Fp080', 'Fp162', 'Separation_cat', 'GroupID', 'GroupSize'])
table.write(args.outtable, format=args.out_format, overwrite=args.overwrite)

# in pixel space
#pp = np.array(wcs.world_to_pixel(SkyCoord(p[:, 0]*u.deg, p[:, 1]*u.deg)))
#qp = np.array(wcs.world_to_pixel(SkyCoord(q[:, 0]*u.deg, q[:, 1]*u.deg)))
#dp = qp-pp
# ax.quiver(pp[0, ~h3], pp[1, ~h3], dp[0, ~h3], dp[1, ~h3], color=C[6], angles='xy',scale_units='xy', scale=1/60.)
# ax.scatter(pp[0, outlier], pp[1, outlier], marker='x', color='lime', alpha=1.0, zorder = -10)

# figure out offset for dvp in pixel space
# qpv = np.array(wcs.world_to_pixel(SkyCoord((p[:, 0]+dvp[:, 0])*u.deg, (p[:, 1]+dvp[:, 1])*u.deg)))
# dpv = qpv - pp
# ax.quiver(pp[0], pp[1], 60*dpv[0], 60*dpv[1], color='grey', alpha=0.5)
