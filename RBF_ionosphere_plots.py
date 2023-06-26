"""
Plot RBF solution given matched file
FIXME Write ellipse parameters out to same (or separate) file.
"""
import os
import argparse
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from numpy.linalg import norm
from astropy.io import fits
from astropy.table import Table
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy import units as u

def transform_rbf(p, q, v, alpha=1):
    w = norm((p - v), axis=1) ** (-2 * alpha) # figure out the weights for the different sources
    d = q-p
    return v + np.sum(d*w[:, None], axis=0)/sum(w)

def semihex(data, axis=None):
    """
    Calculate standard deviation via semi-interhexile range.
    """
    h1, h5 = np.percentile(data, (100/6., 500/6.), axis=axis)
    return (h5-h1)/2.

C = (
    '#000000',
    '#0072b2',
    '#56b4e9',
    '#009e73',
    '#cc79a7',
    '#d55e00',
    '#e69f00',
    '#f0e442')
 
parser = argparse.ArgumentParser()
parser.add_argument('intable', help='Input table')
parser.add_argument('infits', help='Input FITS image (for WCS)')
parser.add_argument('--outformat', default="png", help="image format (default: %(default)s)")
parser.add_argument('--extent', default=3.5, help="plot size in arcminutes (default: %(default)s)")
parser.add_argument('--beam', default='pbcor_norm', help="beam column (default: %(default)s)")
parser.add_argument('--complex', default='complex', help="Boolean column denoting 'complex' sources (default: %(default)s)")
parser.add_argument('--outlier', default='outlier', help="Boolean column denoting 'outlier' sources (default: %(default)s)")

args = parser.parse_args()

table = Table.read(args.intable)
tabarray = table.as_array()
n = len(tabarray)

root = os.path.splitext(args.intable)[0]

header = fits.open(args.infits)[0].header
bmaj, bmin, bpa = 60*header['BMAJ'], 60*header['BMIN'], header['BPA']


# boolean flags
vlss_complex = tabarray[args.complex]
outlier = tabarray[args.outlier]
# classify by beam
h = tabarray[args.beam] > 0.1
fit = ~vlss_complex & ~outlier & h

p = np.stack((tabarray['x'][fit], tabarray['y'][fit]), axis=-1)
q = np.stack((tabarray['x_cat'][fit], tabarray['y_cat'][fit]), axis=-1)
d = q-p
h1 = tabarray[args.beam][fit] > 0.5
h2 = tabarray[args.beam][fit] > 0.25
h3 = tabarray[args.beam][fit] > 0.1

# Find the offset for each source with that source excluded from the fit as a diagnostic
dvp = np.zeros(p.shape)
for i in range(len(p)):
    v = p[i]
    dvp[i] = transform_rbf(np.delete(p, i, axis=0), np.delete(q, i, axis=0), v, 2)
    dvp[i] -= v

# get model for sources excluded from the fit
pc = np.stack((tabarray['x'][~fit], tabarray['y'][~fit]), axis=-1)
qc = np.stack((tabarray['x_cat'][~fit], tabarray['y_cat'][~fit]), axis=-1)
dc = qc-pc
dvc = np.zeros(pc.shape)
for i in range(len(pc)):
    v = pc[i]
    dvc[i] = transform_rbf(p, q, v, 2)
    dvc[i] -= v
hc1 = tabarray[args.beam][~fit] > 0.5
hc2 = tabarray[args.beam][~fit] > 0.25
hc3 = tabarray[args.beam][~fit] > 0.1

fig = plt.figure(figsize=(6, 6), dpi=160)
#ax = plt.gca()
wcs = WCS(header).celestial
ax = fig.add_subplot(111, projection=wcs)
ax.quiver(p[h1, 0], p[h1, 1], d[h1, 0], d[h1, 1], color=C[0], angles='xy',scale_units='xy', scale=1/60.)
ax.quiver(p[h2&~h1, 0], p[h2&~h1, 1], d[h2&~h1, 0], d[h2&~h1, 1], color=C[1], angles='xy', scale_units='xy', scale=1/60.)
ax.quiver(p[h3&~h2, 0], p[h3&~h2, 1], d[h3&~h2, 0], d[h3&~h2, 1], color=C[4], angles='xy',scale_units='xy', scale=1/60.)

ax.quiver(pc[hc1, 0], pc[hc1, 1], dc[hc1, 0], dc[hc1, 1], color=C[0], angles='xy',scale_units='xy', scale=1/60.)
ax.quiver(pc[hc2&~hc1, 0], pc[hc2&~hc1, 1], dc[hc2&~hc1, 0], dc[hc2&~hc1, 1], color=C[1], angles='xy', scale_units='xy', scale=1/60.)
ax.quiver(pc[hc3&~hc2, 0], pc[hc3&~hc2, 1], dc[hc3&~hc2, 0], dc[hc3&~hc2, 1], color=C[4], angles='xy',scale_units='xy', scale=1/60.)
ax.quiver(pc[~hc3, 0], pc[~hc3, 1], dc[~hc3, 0], dc[~hc3, 1], color=C[6], angles='xy',scale_units='xy', scale=1/60.)

ax.scatter(tabarray['x'][outlier], tabarray['y'][outlier], marker='x', color='lime', alpha=1.0, zorder = -10)
ax.scatter(tabarray['x'][vlss_complex], tabarray['y'][vlss_complex], marker='+', color='lime', alpha=1.0, zorder=-10)
ax.quiver(p[:, 0], p[:, 1], dvp[:, 0], dvp[:, 1], color='grey', alpha=0.5, angles='xy',scale_units='xy', scale=1/60., zorder=20)
ax.quiver(pc[:, 0], pc[:, 1], dvc[:, 0], dvc[:, 1], color='grey', alpha=0.5, angles='xy',scale_units='xy', scale=1/60., zorder=20)
ax.grid()
ax.set_xlim([0, header['NAXIS1']])
ax.set_ylim([0, header['NAXIS2']])
ax.set_xlabel("RA")
ax.set_ylabel("Decl.")
#plt.tight_layout()
plt.savefig("%s_map.%s" % (root, args.outformat))

#FIXME cut off a certain distance from the centre of the image?
#can we get the primary beam correction factor for each source and filter on that???

d2 = 60*abs(header['CDELT1'])*d
fig = plt.figure(figsize=(3, 3), dpi=160)
ax = fig.add_subplot(111, aspect='equal')

x = np.median(d2[:, 0])
y = np.median(d2[:, 1])
a = semihex(d2[:, 0])
b = semihex(d2[:, 1])

ell = Ellipse(xy=[x, y], width=2*a, height=2*b, angle=0., zorder=100)
ell.set_color('black')
ell.set_facecolor('none')
ell.set_linewidth(1)
ax.add_artist(ell)

ell1 = Ellipse(xy=[0, 0], width=bmaj, height=bmin, angle=bpa, zorder=100)
ell1.set_color('black')
ell1.set_facecolor('none')
ell1.set_linewidth(1)
#ell1.set_linestyle(':')
ax.add_artist(ell1)

ax.plot(d2[h1, 0], d2[h1, 1], '+', color='grey', zorder=40)
ax.plot(d2[h2&~h1, 0], d2[h2&~h1, 1], '+', color=C[1], zorder=30)
ax.plot(d2[h3&~h2, 0], d2[h3&~h2, 1], '+', color=C[4], zorder=20)
ax.set_xlim([-args.extent, args.extent])
ax.set_ylim([-args.extent, args.extent])
ax.invert_xaxis()
plt.title("x=%+.4g y=%+.4g\na=%.4g b=%.4g" % (x, y, a, b))
plt.xlabel('RA offset/arcmin')
plt.ylabel('Dec offset/arcmin')
plt.tight_layout()
plt.savefig("%s_xy_raw.%s" % (root, args.outformat))

d2 = 60*abs(header['CDELT1'])*(d-dvp)

fig = plt.figure(figsize=(3, 3), dpi=160)
ax = fig.add_subplot(111, aspect='equal')

x = np.median(d2[:, 0])
y = np.median(d2[:, 1])
a = semihex(d2[:, 0])
b = semihex(d2[:, 1])

ell = Ellipse(xy=[x, y], width=2*a, height=2*b, angle=0., zorder=100)
ell.set_color('black')
ell.set_facecolor('none')
ell.set_linewidth(1)
ax.add_artist(ell)

ell1 = Ellipse(xy=[0, 0], width=bmaj, height=bmin, angle=bpa, zorder=100)
ell1.set_color('black')
ell1.set_facecolor('none')
ell1.set_linewidth(1)
ax.add_artist(ell1)

ax.plot(d2[h1, 0], d2[h1, 1], '+', color='grey', zorder=40)
ax.plot(d2[h2&~h1, 0], d2[h2&~h1, 1], '+', color=C[1], zorder=30)
ax.plot(d2[h3&~h2, 0], d2[h3&~h2, 1], '+', color=C[4], zorder=20)
ax.set_xlim([-args.extent, args.extent])
ax.set_ylim([-args.extent, args.extent])
ax.invert_xaxis()
plt.title("a=%.4g b=%.4g" % (a, b))
plt.xlabel('RA offset/arcmin')
plt.ylabel('Dec offset/arcmin')
plt.tight_layout()
plt.savefig("%s_xy_corr.%s" % (root, args.outformat))
