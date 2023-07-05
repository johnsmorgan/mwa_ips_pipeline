#!/usr/bin/env python3

import os
import argparse
import logging

import numpy as np
from scipy.interpolate import RectBivariateSpline
from scipy.optimize import minimize

import astropy.units as u
from astropy.io import fits
from astropy.table import Table
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord

parser = argparse.ArgumentParser()
parser.add_argument('infile', help='Input image')
parser.add_argument('intable', help='Input table')
parser.add_argument('outtable', help='Output table')
parser.add_argument('--ra', default="ra", help="RA Column")
parser.add_argument('--dec', default="dec", help="Decl. Column")
parser.add_argument('--peak_flux', default="peak_flux", help="Peak Flux")
parser.add_argument('--background', default="background", help="Background (not modified)")
parser.add_argument('--flag_column', default="residual_mean", help="fit only where this column is flagged")
parser.add_argument('--ofmt', default="votable", help="output file format")
parser.add_argument('--overwrite', action='store_true', help="overwrite")
parser.add_argument("--cutoff", dest="cutoff", default=5, help="remove sources with lower S/N")
parser.add_argument("-v", "--verbose", action="count", dest="verbose", default=0, help="-v info, -vv debug")

args = parser.parse_args()

if args.verbose == 0:
    logging.basicConfig(format='%(asctime)s-%(levelname)s %(message)s', level=logging.WARNING)
elif args.verbose == 1:
    logging.basicConfig(format='%(asctime)s-%(levelname)s %(message)s', level=logging.INFO)
else:
    logging.basicConfig(format='%(asctime)s-%(levelname)s %(message)s', level=logging.DEBUG)

root, ext = os.path.splitext(args.infile)

hdus = fits.open(args.infile)
tab = Table.read(args.intable)
snr = tab['peak_flux'] / tab['local_rms']
tab = tab[snr > args.cutoff]

wcs = WCS(hdus[0].header).celestial
data = hdus[0].data

if not args.overwrite and os.path.exists(args.outtable):
    raise IOError("outtable exists")

skycoords = SkyCoord(tab['ra'].data.data*u.deg, tab['dec'].data.data*u.deg)
mask = tab[args.flag_column].mask

xf, yf = wcs.wcs_world2pix(skycoords.ra.deg, skycoords.dec.deg, 0)
y = np.round(yf).astype(np.int)
x = np.round(xf).astype(np.int)

xx = np.array([-1., 0., 1])
peak_flux = np.zeros(len(x), dtype=np.float32)
x_out = np.zeros(len(x), dtype=np.float32)
y_out = np.zeros(len(x), dtype=np.float32)
niter = np.zeros(len(x), dtype=int)
flag = np.zeros(len(x), dtype=int)

vertices = np.array([[-np.sqrt(3)/4, -0.25], [0, 0.5], [np.sqrt(3)/4, -0.25]])

for i in range(len(x)):
    if ~mask[i]:
        flag[i] = -1
        logging.info("%s err:%d -- not masked -- skipping", tab['uuid'][i], flag[i])
        continue
    s = (0, 0, slice(y[i]-1, y[i]+2), slice(x[i]-1, x[i]+2))
    d = data[s]
    if not d.shape == (3,3):
        flag[i] = 1
        logging.warning("%s err:%d -- invalid shape -- skipping", tab['uuid'][i], flag[i])
        continue
    interp = RectBivariateSpline(xx,xx,d, kx=2,ky=2)
    coords = (yf[i]-y[i], xf[i]-x[i])
    f = lambda x: -interp(x[0], x[1])[0][0]
    min_ = minimize(fun=f, x0=(0, 0), method='Nelder-Mead', 
                    options={'xatol': 0.01, 'initial_simplex':vertices})
    if not min_['success']:
        flag[i] = 2
        logging.warning("%s err:%d -- fit failed in %d iterations -- %s", tab['uuid'][i], flag[i], min_['nit'], min_['message'])
        continue
    peak_flux[i] = -min_['fun']
    y_out[i], x_out[i] = min_['x']
    if np.abs(x_out[i]) > 1 or np.abs(y_out[i]) > 1:
        flag[i] = 3
        logging.warning("%s err:%d -- interp position outside pixel at %d,%d. %d iterations -- %s", tab['uuid'][i], flag[i], x_out[i], y_out[i], min_['nit'], min_['message'])
    else:
        logging.debug("%s err:%d -- %d iterations -- %s", tab['uuid'][i], flag[i], min_['nit'], min_['message'])

replace = mask & (flag == 0)
xy = np.stack((x+x_out, y+y_out)).swapaxes(0, 1)
skycoords2 = wcs.celestial.wcs_pix2world(xy, 0)
tab[args.peak_flux][:] = np.where(replace, peak_flux-tab[args.background], tab[args.peak_flux][:])
tab[args.ra][:] = np.where(replace, skycoords2[:, 0], tab[args.ra][:])
tab[args.dec][:] = np.where(replace, skycoords2[:, 1], tab[args.dec][:])
tab['pos_interp_flag'] = flag
tab.write(args.outtable, format=args.ofmt, overwrite=args.overwrite)
