#!/usr/bin/env python
"""
Make an obsid-specific version of a catalogue
Only include sources that lie within image (and, optionally above a pb threshold)
"""
import os
import logging
import numpy as np
from astropy.table import Table
from astropy.coordinates import SkyCoord
from imstack import ImageStack
from scipy.optimize import minimize


from optparse import OptionParser, OptionValueError

parser = OptionParser(usage = "usage: %prog input.hdf5 input.vot output.vot" +
"""

add various columns and delete unneeded ones.
""")
parser.add_option("-p", "--pb_threshold", dest="pb", default=0.25, help="only keep sources within this threshold")
parser.add_option("--ra_col", dest="ra_col", default='ra', help="ra column in input")
parser.add_option("--dec_col", dest="dec_col", default='dec', help="dec column in input")
parser.add_option("-v", "--verbose", action="count", dest="verbose", default=0, help="-v info, -vv debug")

opts, args = parser.parse_args()
if not len(args) == 3:
    raise OptionValueError("expects 3 arguments")

if opts.verbose == 0:
    logging.basicConfig(format='%(asctime)s-%(levelname)s %(message)s', level=logging.WARNING)
elif opts.verbose == 1:
    logging.basicConfig(format='%(asctime)s-%(levelname)s %(message)s', level=logging.INFO)
else:
    logging.basicConfig(format='%(asctime)s-%(levelname)s %(message)s', level=logging.DEBUG)

if os.path.exists(args[2]):
    os.remove(args[2])

imstack = ImageStack(args[0], freq='121-132', image_type=None)
dim_x, dim_y = imstack.group['beam'].shape[1:3]

t = Table.read(args[1])
logging.debug("%d rows in master", len(t))

logging.info("calculating primary beam max")
f = lambda x: -imstack.pix2beam(np.int_(np.round(x[0])), np.int_(np.round(x[1])), scale=True)
b=f((1200.0, 1200.0))
min_ = minimize(fun=f, x0=(1200.0, 1200.0), method='Nelder-Mead', options={'xatol': 1})
pbmax = -min_['fun']

logging.info("calculating primary beam for each source")
t["pbcor"] = np.nan*np.ones(len(t))
t["x"] = np.nan*np.ones(len(t))
t["y"] = np.nan*np.ones(len(t))
# loop over all unmasked values
n_infield=0
try:
    m = ~t[opts.ra_col].mask
except AttributeError:
    m = np.ones_like(t[opts.ra_col], dtype=bool)

x, y = imstack.wcs.celestial.wcs_world2pix(t[opts.ra_col].data, t[opts.dec_col].data, 0)
#print(x)
infield = np.isfinite(x) & np.isfinite(y) & (x>=0) & (x < dim_x-1) & (y>=0) & (y<dim_y-1)
for s in np.argwhere(m & infield)[:, 0]:
    #x, y = imstack.world2pix(t[opts.ra_col][s], t[opts.dec_col][s])
    #print(s, sep=' ')
    #print(x[s],y[s])
    #if x<0 or x >= dim_x:
    #    continue
    #if y<0 or y >= dim_y:
    #    continue
    n_infield += 1
    t["x"][s] = x[s]
    t["y"][s] = y[s]
    t["pbcor"][s] = imstack.pix2beam(int(np.round(x[s])), int(np.round(y[s])), scale=True)
    logging.debug("pbcor: %f", t["pbcor"][s])

logging.info("{n_infield} in field")
t["pbcor_norm"] = t["pbcor"] / pbmax
t = t[t["pbcor_norm"]>=opts.pb]
logging.info(f"len(t) above pb threshold")
if len(t) > 0:
    t.write(args[2], format='votable')
else:
    logging.warning("len table = %d ... not writing output file!", {len(t)})
