#!/usr/bin/env python

import sys, os
import numpy as np

from astropy.io import votable
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from abs_scale import get_scale

IN_DIR="."
OBSID=sys.argv[1]
FREQ=sys.argv[2]
POL = sys.argv[3]
CENTRE=0.9
EDGE=0.1
SNR_THRESH=10

cal =votable.parse_single_table(os.path.join(IN_DIR, "{}_{}-{}-image_cal.vot".format(OBSID, FREQ, POL))).to_table()
scale, frac_error, n = get_scale(cal, SNR_THRESH, CENTRE)

plt.figure(figsize=(10,8))
plt.title("{}".format(POL))
plt.grid(True)
#plt.scatter(np.where(cal['ra']<180, cal['ra'], cal['ra']-360), cal['dec'], c =cal['peak_flux']/cal['pbcor']/cal['Fp162'],
#            alpha=0.9, cmap=plt.cm.get_cmap('viridis'), vmax=2, vmin=0.5, norm=LogNorm())
max_pb = np.max(cal['pbcor'])
cat = cal[cal['pbcor'] > CENTRE*max_pb]
plt.scatter(cat['ra'], cat['dec'], c=scale*cat['peak_flux']/cat['pbcor']/cat['Fp162'], marker='+',
            alpha=0.9, cmap=plt.cm.get_cmap('viridis'), vmax=2, vmin=0.5, norm=LogNorm())
cat = cal[(cal['pbcor'] <= CENTRE*max_pb) & (cal['pbcor'] >= EDGE*max_pb)]
plt.scatter(cat['ra'], cat['dec'], c=scale*cat['peak_flux']/cat['pbcor']/cat['Fp162'],
            alpha=0.9, cmap=plt.cm.get_cmap('viridis'), vmax=2, vmin=0.5, norm=LogNorm())
cat = cal[cal['pbcor'] < EDGE*max_pb]
plt.scatter(cat['ra'], cat['dec'], c=scale*cat['peak_flux']/cat['pbcor']/cat['Fp162'], marker='x',
            alpha=0.9, cmap=plt.cm.get_cmap('viridis'), vmax=2, vmin=0.5, norm=LogNorm())
plt.cscale=('log')
plt.xlim(plt.xlim()[::-1]) # flip x axis
plt.clim(0.5, 2)
plt.colorbar()
plt.savefig("{}_{}_{}_image_pb_err.png".format(OBSID, FREQ, POL))
