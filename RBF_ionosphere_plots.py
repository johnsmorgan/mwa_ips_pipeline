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
from astropy.io.votable import parse
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import Longitude, SkyCoord
from astropy import units as u

EXTENT=3.5
 
parser = argparse.ArgumentParser()
parser.add_argument('intable', help='Input table')
parser.add_argument('infits', help='Input FITS image (for WCS)')
parser.add_argument('--outformat', default="png", help="image format ")
parser.add_argument('--extent', default=EXTENT, help="plot size in arcminutes")
parser.add_argument('--ra', default='ra', help="Apparant RA column")
parser.add_argument('--dec', default='dec', help="Apparant Dec column")
parser.add_argument('--ra_cat', default='ra_cat', help="Catalogued RA column")
parser.add_argument('--dec_cat', default='dec_cat', help="Catalogued Dec column")
parser.add_argument('--complex', default='complex', help="Boolean column denoting 'complex' sources")

args = parser.parse_args()

votable = parse(args.intable)
table = votable.get_first_table()

root = os.path.splitext(args.intable)[0]

header = fits.open(args.infits)[0].header
bmaj, bmin, bpa = 60*header['BMAJ'], 60*header['BMIN'], header['BPA']

# select those sources with simple morphology

if 'complex' in table.array.dtype.names:
    simple = ~table.array[args.complex]
else:
    simple = np.ones(len(table.array), dtype=np.bool)

ion_map = table.array[~table.array.mask[args.ra_cat] & simple]

if np.mean(np.cos(Longitude(ion_map[args.ra_cat]*u.deg))) > 0:
    wrap_angle=180.*u.deg
else:
    wrap_angle=360.*u.deg

p = np.stack((Longitude(ion_map[args.ra_cat]*u.deg, wrap_angle=wrap_angle).deg,
              ion_map[args.dec_cat]), axis=-1)
q = np.stack((Longitude(ion_map[args.ra]*u.deg, wrap_angle=wrap_angle).deg,
              ion_map[args.dec]), axis=-1)
d = q-p

vlss_complex = table.array[~table.array.mask[args.ra_cat] & ~simple]

pc = np.stack((Longitude(vlss_complex[args.ra_cat]*u.deg, wrap_angle=wrap_angle).deg,
              vlss_complex[args.dec_cat]), axis=-1)
qc = np.stack((Longitude(vlss_complex[args.ra]*u.deg, wrap_angle=wrap_angle).deg,
              vlss_complex[args.dec]), axis=-1)

def transform_rbf(p, q, v, alpha=1):
    n = len(p)
    w = norm((p - v), axis=1) ** (-2 * alpha) # figure out the weights for the different sources
    d = q-p
    return v + np.sum(d*w[:, None], axis=0)/sum(w)

def semihex(data, axis=None):
    """
    Calculate standard deviation via semi-interhexile range.
    """
    h1, h5 = np.percentile(data, (100/6., 500/6.), axis=axis)
    return (h5-h1)/2.


# Find the offset for each source with that source excluded from the fit as a diagnostic

dvp = np.zeros(p.shape)
for i in range(len(p)):
    v = p[i]
    dvp[i] = transform_rbf(np.delete(p, i, axis=0), np.delete(q, i, axis=0), v, 2)
    dvp[i] -= v

# sources with non-simple vlss morphology are excluded from the fit, but we want to work out modelled positions for them.
dvc = np.zeros(pc.shape)
for i in range(len(pc)):
    v = pc[i]
    dvc[i] = transform_rbf(p, q, v, 2)
    dvc[i] -= v

fig = plt.figure(figsize=(6, 6), dpi=160)
#ax = plt.gca()
wcs = WCS(header).celestial
ax = fig.add_subplot(111, projection=wcs)
pp = np.array(wcs.world_to_pixel(SkyCoord(p[:, 0]*u.deg, p[:, 1]*u.deg)))
qp = np.array(wcs.world_to_pixel(SkyCoord(q[:, 0]*u.deg, q[:, 1]*u.deg)))
dp = qp-pp
#dc = qc-pc
ax.quiver(pp[0], pp[1], 60*dp[0], 60*dp[1])
# figure out offset for dvp in pixel space
qpv = np.array(wcs.world_to_pixel(SkyCoord((p[:, 0]+dvp[:, 0])*u.deg, (p[:, 1]+dvp[:, 1])*u.deg)))
dpv = qpv - pp
ax.quiver(pp[0], pp[1], 60*dpv[0], 60*dpv[1], color='blue', alpha=0.5)
ax.grid()

#plt.axes().set_aspect('equal')
ax.set_xlabel("RA (degrees)")
ax.set_ylabel("Decl. (degrees)")
plt.savefig("%s_map.%s" % (root, args.outformat))

#FIXME cut off a certain distance from the centre of the image?
#can we get the primary beam correction factor for each source and filter on that???

d2 = 60*d
fig = plt.figure(figsize=(3, 3), dpi=160)
ax = fig.add_subplot(111, aspect='equal')

x = np.mean(d2[:, 0])
y = np.mean(d2[:, 1])
a = semihex(d2[:, 0])
b = semihex(d2[:, 1])

ell = Ellipse(xy=[x, y], width=2*a, height=2*b, angle=0., zorder=20)
ell.set_color('black')
ell.set_facecolor('none')
ell.set_linewidth(1)
ax.add_artist(ell)
print("Ellipse parameters: x=%g, y=%g, semi_a=%g, semi_b=%g" % (x, y, a, b))

ell1 = Ellipse(xy=[0, 0], width=bmaj, height=bmin, angle=bpa, zorder=30)
ell1.set_color('black')
ell1.set_facecolor('none')
ell1.set_linewidth(1)
#ell1.set_linestyle(':')
ax.add_artist(ell1)

ax.plot(d2[:, 0], d2[:, 1], '+', color='grey', zorder=10)
ax.set_xlim([-args.extent, args.extent])
ax.set_ylim([-args.extent, args.extent])
plt.xlabel('RA offset/arcmin')
plt.ylabel('Dec offset/arcmin')
plt.tight_layout()
plt.savefig("%s_xy_raw.%s" % (root, args.outformat))

d2 = 60*(d-dvp)

fig = plt.figure(figsize=(3, 3), dpi=160)
ax = fig.add_subplot(111, aspect='equal')

x = np.mean(d2[:, 0])
y = np.mean(d2[:, 1])
a = semihex(d2[:, 0])
b = semihex(d2[:, 1])

ell = Ellipse(xy=[x, y], width=2*a, height=2*b, angle=0., zorder=20)
ell.set_color('black')
ell.set_facecolor('none')
ell.set_linewidth(1)
ax.add_artist(ell)
print("Ellipse parameters: x=%g, y=%g, semi_a=%g, semi_b=%g" % (x, y, a, b))

ell1 = Ellipse(xy=[0, 0], width=bmaj, height=bmin, angle=bpa, zorder=31)
ell1.set_color('black')
ell1.set_facecolor('none')
ell1.set_linewidth(1)
ax.add_artist(ell1)

ax.plot(d2[:, 0], d2[:, 1], '+', color='grey', zorder=10)
ax.set_xlim([-args.extent, args.extent])
ax.set_ylim([-args.extent, args.extent])
plt.xlabel('RA offset/arcmin')
plt.ylabel('Dec offset/arcmin')
plt.tight_layout()
plt.savefig("%s_xy_corr.%s" % (root, args.outformat))
