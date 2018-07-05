"""
Plot RBF solution given matched file
FIXME read beam from fits file (dependency on fits file)
"""
import os, sys
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from numpy.linalg import norm
from astropy.io.votable import parse
from astropy.io import fits
from astropy.coordinates import Longitude
from astropy import units as u
#from scipy.stats import norm

from scipy.interpolate import LSQBivariateSpline, SmoothBivariateSpline

LIM={'121-132': (-3.5, 3.5), '057-068': (-7.0, 7.0)}

votable = parse(sys.argv[1])
freq=sys.argv[2]
fitsfile=sys.argv[3]
format=sys.argv[4]
table = votable.get_first_table()
root=os.path.splitext(sys.argv[1])[0]

header=fits.open(fitsfile)[0].header
bmaj, bmin, bpa = 60*header['BMAJ'], 60*header['BMIN'], header['BPA']

#select those sources with simple morphology which is detected in both lo and hi

ion_map = table.array[~table.array.mask['ra_cat'] & ~table.array['complex']]

p = np.stack((Longitude(ion_map['ra_cat']*u.deg, wrap_angle=180*u.deg),
              ion_map['dec_cat']), axis=-1)
q = np.stack((Longitude(ion_map['ra']*u.deg, wrap_angle=180*u.deg),
              ion_map['dec']), axis=-1)

vlss_complex = table.array[~table.array.mask['ra_cat'] & table.array['complex']]

pc = np.stack((np.where(vlss_complex['ra_cat'] > 180, vlss_complex['ra_cat']-360, vlss_complex['ra_cat']),
              vlss_complex['dec_cat']), axis=-1)
qc = np.stack((np.where(vlss_complex['ra'] > 180, vlss_complex['ra']-360, vlss_complex['ra']),
              vlss_complex['dec']), axis=-1)

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

plt.figure(figsize=(6, 6))
ax = plt.gca()
d = q-p
dc = qc-pc
#ax.quiver(pc[:, 0], pc[:, 1], dc[:, 0], dc[:, 1], angles='xy',scale_units='xy',scale=1/60., color='gray')
ax.quiver(p[:, 0], p[:, 1], d[:, 0], d[:, 1], angles='xy',scale_units='xy',scale=1/60.)
ax.quiver(p[:, 0], p[:, 1], dvp[:, 0], dvp[:, 1], angles='xy',scale_units='xy',scale=1/60., color='blue', alpha=0.5)
ax.invert_xaxis()
labels = ax.get_xticks().tolist()
#labels = [l if float(l) >= 0 else str(float(l)+360)  for l in labels)]
labels = ["" if i%2==1 else l if float(l) >= 0 else str(float(l)+360)  for i, l in enumerate(labels)]
ax.set_xticklabels(labels)

plt.axes().set_aspect('equal')
ax.set_xlabel("RA (degrees)")
ax.set_ylabel("Decl. (degrees)")
plt.savefig("%s_map%s" % (root, format))

#FIXME cut off a certain distance from the centre of the image?
#can we get the primary beam correction factor for each source and filter on that???

d2 = 60*d
fig = plt.figure(figsize=(3, 3))
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
print "Ellipse parameters: x=%g, y=%g, semi_a=%g, semi_b=%g" % (x, y, a, b)

ell1 = Ellipse(xy=[0, 0], width=bmaj, height=bmin, angle=bpa, zorder=30)
ell1.set_color('black')
ell1.set_facecolor('none')
ell1.set_linewidth(1)
#ell1.set_linestyle(':')
ax.add_artist(ell1)

ax.plot(d2[:, 0], d2[:, 1], '+', color='grey', zorder=10)
ax.set_xlim(LIM[freq])
ax.set_ylim(LIM[freq])
plt.xlabel('RA offset/arcmin')
plt.ylabel('Dec offset/arcmin')
plt.tight_layout()
plt.savefig("%s_xy_raw%s" % (root, format))

#for i, label in enumerate(['x', 'y']):
#    var = d2[:, i]
#    plt.figure(figsize=(4, 4))
#    _, x, _ = plt.hist(var, bins=20, normed=True)
#    mu = np.mean(var)
#    sigma = np.std(var)
#    sh = semihex(var)
#    plt.plot(x, norm.pdf(x, mu, sigma))
#    plt.plot(x, norm.pdf(x, mu, sigma))
#    print "mean=%f, std=%f, semihex=%g" % (mu, sigma, sh)


d2 = 60*(d-dvp)

fig = plt.figure(figsize=(3, 3))
ax = fig.add_subplot(111, aspect='equal')
#d_sd_x = semihex(d2[:, 0])
#d_sd_y = semihex(d2[:, 1])

x = np.mean(d2[:, 0])
y = np.mean(d2[:, 1])
a = semihex(d2[:, 0])
b = semihex(d2[:, 1])

ell = Ellipse(xy=[x, y], width=2*a, height=2*b, angle=0., zorder=20)
#ell.set_alpha(0)
ell.set_color('black')
ell.set_facecolor('none')
ell.set_linewidth(1)
ax.add_artist(ell)
print "Ellipse parameters: x=%g, y=%g, semi_a=%g, semi_b=%g" % (x, y, a, b)

ell1 = Ellipse(xy=[0, 0], width=bmaj, height=bmin, angle=bpa, zorder=31)
ell1.set_color('black')
ell1.set_facecolor('none')
ell1.set_linewidth(1)
#ell1.set_linestyle(':')
ax.add_artist(ell1)

ax.plot(d2[:, 0], d2[:, 1], '+', color='grey', zorder=10)
ax.set_xlim(LIM[freq])
ax.set_ylim(LIM[freq])
plt.xlabel('RA offset/arcmin')
plt.ylabel('Dec offset/arcmin')
plt.tight_layout()
plt.savefig("%s_xy_corr%s" % (root, format))
