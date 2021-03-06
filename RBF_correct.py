#!/usr/bin/env python
import os
import numpy as np
from numpy import linalg as la
from astropy.io.votable import parse
from astropy.coordinates import Longitude
from astropy import units as u
from optparse import OptionParser

def transform_rbf(p, q, v, alpha=1, reverse=False):
    n = len(p)
    distance = la.norm(p - v, axis=1)
    if np.any(distance == 0.):
        w = np.where(distance == 0., 1., 0.)
    else:
        w = distance ** (-2 * alpha) # figure out the weights for the different sources
    d = q-p
    if reverse:
        sign = -1.
    else:
        sign = 1.
    return v + sign*np.sum(d*w[:, None], axis=0)/sum(w)

parser = OptionParser(usage = "usage: %prog model.vot input.vot" +
"""
Using the Add RA_corr and DE_corr
""")
parser.add_option("--ra_raw", default="ra", dest="ra_raw", help="name of uncorrected RA column in model file")
parser.add_option("--de_raw", default="dec", dest="dec_raw", help="name of uncorrected Decl. column in model file")
parser.add_option("--ra_cat", default="ra_cat", dest="ra_cat", help="name of correct RA column in model file")
parser.add_option("--de_cat", default="dec_cat", dest="dec_cat", help="name of correct decl. column in model file")
parser.add_option("--ra_in", default="ra", dest="ra_in", help="name of RA column in input file")
parser.add_option("--de_in", default="dec", dest="dec_in", help="name of Decl. column in input file")
parser.add_option("--ra_out", default="ra_corr", dest="ra_out", help="name of RA column in output file")
parser.add_option("--de_out", default="dec_corr", dest="dec_out", help="name of Decl. column in output file")
parser.add_option("--bad", default="bad", dest="bad", help="name of complex flag column in model file")
parser.add_option("--cat_out_fmt", default='votable', dest="cat_fmt", help="format of output catalog")
parser.add_option("--alpha", default=2.0, dest="alpha", type="float", help="RBF alpha (default=%default)")
parser.add_option("--reverse", dest="reverse", action="store_true", help="Reverse correction (e.g. make astrometrically catalogue match distorted image)")

opts, args = parser.parse_args()
# read in master table
map_table = parse(args[0]).get_first_table()

in_table = parse(args[1]).get_first_table()

if os.path.exists(args[2]):
    os.remove(args[2])

#select those sources with simple morphology which is detected in both lo and hi
if opts.bad in map_table.array.dtype.names:
    simple = ~map_table.array[opts.bad]
else:
    simple = np.ones(len(map_table.array), dtype=np.bool)

ion_map = map_table.array[~map_table.array.mask[opts.ra_cat] & simple]

if np.mean(np.cos(Longitude(ion_map['ra_cat']*u.deg))) > 0:
    wrap_angle=180.*u.deg
else:
    wrap_angle=360.*u.deg

p = np.stack((Longitude(ion_map[opts.ra_cat]*u.deg, wrap_angle=wrap_angle).deg,
              ion_map[opts.dec_cat]), axis=-1)
q = np.stack((Longitude(ion_map[opts.ra_raw]*u.deg, wrap_angle=wrap_angle).deg,
              ion_map[opts.dec_raw]), axis=-1)

pc = np.stack((Longitude(in_table.array[opts.ra_in], wrap_angle=wrap_angle, unit=u.deg).deg,
              in_table.array[opts.dec_in]), axis=-1)

# transform points
dvc = np.zeros(pc.shape)
for i in range(len(pc)):
    v = pc[i]
    try:
        dvc[i] = transform_rbf(q, p, v, opts.alpha, opts.reverse)
    except:
        print(i)
        print(pc)
        print(pc[i-1])
        print(transform_rbf(q, p, v, opts.alpha, opts.reverse))
        print(transform_rbf(q, p, pc[i-1], opts.alpha, opts.reverse))
        raise

in_table = in_table.to_table()
in_table[opts.ra_out] = Longitude(dvc[:, 0]*u.deg, wrap_angle=360*u.deg)
in_table[opts.dec_out] = dvc[:, 1]*u.deg
in_table.write(args[2], format=opts.cat_fmt)
