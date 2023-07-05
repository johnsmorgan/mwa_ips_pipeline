#!/usr/bin/env python3

import os
import argparse
import logging

import numpy as np
from scipy.interpolate import RectBivariateSpline

import astropy.units as u
from astropy.io import fits
from astropy.table import Table
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord

parser = argparse.ArgumentParser()
parser.add_argument('infile', help='Input image')
parser.add_argument('intable', help='Input table')
parser.add_argument('outfile', help='Output table')
parser.add_argument('--ra', default="ra", help="RA Column")
parser.add_argument('--dec', default="dec", help="Decl. Column")
parser.add_argument('--ofmt', default="votable", help="output file format")
parser.add_argument('--overwrite', action='store_true', help="overwrite")
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
bkg_hdus = fits.open(root+"_bkg"+ext)
rms_hdus = fits.open(root+"_rms"+ext)

tab = Table.read(args.intable)
wcs = WCS(hdus[0].header).celestial
data = hdus[0].data
bkg_wcs = WCS(bkg_hdus[0].header).celestial
rms_wcs = WCS(rms_hdus[0].header).celestial
bkg = bkg_hdus[0].data
rms = rms_hdus[0].data

skycoords = SkyCoord(tab['ra'].data.data*u.deg, tab['dec'].data.data*u.deg)

xf, yf = wcs.wcs_world2pix(skycoords.ra.deg, skycoords.dec.deg, 0)
y = np.round(yf).astype(int)
x = np.round(xf).astype(int)

xx = np.array([-1., 0., 1])
offset = np.zeros(len(x))
moment2 = np.zeros(len(x))
local_rms = np.zeros(len(x))
background = np.zeros(len(x))

for i in range(len(x)):
    s = (0, 0, slice(y[i]-1, y[i]+2), slice(x[i]-1, x[i]+2))
    d = data[s]
    if not d.shape == (3,3):
        #print(s)
        #print(d.shape)
        logging.warning("skipping source %d due to bad shape" % i)
        continue
    interp = RectBivariateSpline(xx,xx,d, kx=2,ky=2)
    coords = (yf[i]-y[i], xf[i]-x[i])
    offset[i] = np.hypot(*coords)
    moment2[i] = interp(*coords)[0][0]
    background[i] = bkg[bkg_wcs.world_to_array_index(skycoords[i])]
    local_rms[i]  = rms[rms_wcs.world_to_array_index(skycoords[i])]

tab['pix_offset'] = offset
tab['peak_flux2'] = moment2-background
tab['local_rms2'] = local_rms
tab['background2'] = background
tab.write(args.outfile, format=args.ofmt, overwrite=args.overwrite)
