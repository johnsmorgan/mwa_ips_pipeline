#!/usr/bin/env python

import sys, os
import numpy as np

from astropy.io import votable
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

IN_DIR="."
OBSID=sys.argv[1]
FREQ=sys.argv[2]
POL = sys.argv[3]

cal =votable.parse_single_table(os.path.join(IN_DIR, "{}_{}-{}-image_cal.vot".format(OBSID, FREQ, POL))).to_table()

plt.figure(figsize=(10,8))
plt.title("{}".format(POL))
plt.grid(True)
#plt.scatter(np.where(cal['ra']<180, cal['ra'], cal['ra']-360), cal['dec'], c =cal['peak_flux']/cal['pbcor']/cal['Fp162'],
#            alpha=0.9, cmap=plt.cm.get_cmap('viridis'), vmax=2, vmin=0.5, norm=LogNorm())
plt.scatter(cal['ra'], cal['dec'], c =cal['peak_flux']/cal['pbcor']/cal['Fp162'],
            alpha=0.9, cmap=plt.cm.get_cmap('viridis'), vmax=2, vmin=0.5, norm=LogNorm())
plt.cscale=('log')
plt.xlim(plt.xlim()[::-1]) # flip x axis
plt.clim(0.5, 2)
plt.colorbar()
plt.savefig("{}_{}_{}_image_pb_err.png".format(OBSID, FREQ, POL))
