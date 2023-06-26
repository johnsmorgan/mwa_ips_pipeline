#!/usr/bin/env python
import os
import numpy as np
import astropy.units as u
from astropy.table import Table
from astropy.time import Time
from astropy.coordinates import SkyCoord, get_moon, EarthLocation
from imstack import ImageStack
from scipy.optimize import minimize


from optparse import OptionParser, OptionValueError
LAT=-26.703319
LON=116.67081
ALT=377.0

LOCATION = EarthLocation.from_geodetic(lat=LAT*u.deg, lon=LON*u.deg, height=ALT*u.m)
MOON_RADIUS = 1737.4e3*u.m
POL_OPTIONS=("XX", "YY", "I")

parser = OptionParser(usage = "usage: %prog input.hdf5" +
"""

add various columns and delete unneeded ones.
""")
parser.add_option("-o", "--obsid", dest="obsid", default=None, help="time in gps format used for calculation of Moon location (default: first 10 letters of input.hdf5)")

opts, args = parser.parse_args()

if not opts.obsid:
    opts.obsid = args[0][:10]

time = Time(float(opts.obsid), format='gps')
moon = get_moon(time.utc, location=LOCATION)
print(moon)

imstack = ImageStack(args[0], freq='121-132')
dim_x, dim_y = imstack.group['beam'].shape[1:3]

x, y = imstack.world2pix(moon.ra.deg, moon.dec.deg)
#print(x, dim_x, y, dim_y)
if x>0 and y>0 and x<dim_x and y<dim_y:
    moon_radius_arcm = 60*np.degrees(float(MOON_RADIUS/moon.distance)) # float is to get rid of Quantities once they cancel out
    with open(f"{opts.obsid}.reg", 'w') as f:
        print(f"# Region file format: DS9 version 4.0", file=f)
        print(f"# Moon location at {time.gps:.0f} gps {time.utc.isot[:19]}", file=f)
        print(f"j2000; circle {moon.ra.deg:.5f}d {moon.dec.deg:.5f}d {moon_radius_arcm:.2f}'", file=f)