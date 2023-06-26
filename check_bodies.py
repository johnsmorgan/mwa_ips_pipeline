#!/usr/bin/env python
import os
import numpy as np
import astropy.units as u
from astropy.table import Table
from astropy.time import Time
from astropy.coordinates import solar_system_ephemeris, EarthLocation
from astropy.coordinates import SkyCoord, get_sun, get_moon, get_body
from imstack import ImageStack
from scipy.optimize import minimize


from optparse import OptionParser, OptionValueError

LAT=-26.703319
LON=116.67081
ALT=377.0

LOCATION = EarthLocation.from_geodetic(lat=LAT*u.deg, lon=LON*u.deg, height=ALT*u.m)

parser = OptionParser(usage = "usage: %prog input.hdf5" +
"""
add various columns and delete unneeded ones.
""")
parser.add_option("-o", "--obsid", dest="obsid", default=None, help="time in gps format used for calculation of Moon location (default: first 10 letters of input.hdf5)")
parser.add_option("--header", dest="header", action='store_true', help="print csv header")

opts, args = parser.parse_args()

if not opts.obsid:
    opts.obsid = args[0][:10]

imstack = ImageStack(args[0], freq='121-132')
dim_x, dim_y = imstack.group['beam'].shape[1:3]
ra_dec = SkyCoord(tuple(imstack.wcs.celestial.wcs_pix2world(np.array([[dim_x//2, dim_y//2]]), 0)*u.deg))
#print(ra_dec)
#print(dim_x//2, dim_y//2)

time = Time(float(opts.obsid), format='gps')
outstring=""
if opts.header:
    print("obsid,sun_ra_deg,sun_dec_deg,sun_x,sun_y,sun_elongation_deg,moon_ra_deg,moon_dec_deg,moon_x,moon_y,moon_elongation_deg,jupiter_ra_deg,jupiter_dec_deg,jupiter_x,jupiter_y,jupiter_elongation_deg")

# sun
sun = get_sun(time.utc)
dist = sun.separation(ra_dec)[0].deg
sun_x, sun_y = imstack.world2pix(sun.ra.deg, sun.dec.deg)
if 0<sun_x<dim_x and 0<sun_y<dim_y:
    outstring += f"{opts.obsid},{sun.ra.deg:.5f},{sun.dec.deg:+.5f},{sun_x},{sun_y},{dist}"
else:
    outstring += f"{opts.obsid},,,,,{dist}"

# moon
moon = get_moon(time.utc, location=LOCATION)
dist = moon.separation(ra_dec)[0].deg
moon_x, moon_y = imstack.world2pix(moon.ra.deg, moon.dec.deg)
if 0<moon_x<dim_x and 0<moon_y<dim_y:
    outstring += f",{moon.ra.deg:.5f},{moon.dec.deg:+.5f},{moon_x},{moon_y},{dist}"
else:
    outstring += f",,,,,{dist}"

# jupiter 
with solar_system_ephemeris.set('builtin'):
    jupiter = get_body('jupiter', time.utc, location=LOCATION)
dist = jupiter.separation(ra_dec)[0].deg
jupiter_x, jupiter_y = imstack.world2pix(jupiter.ra.deg, jupiter.dec.deg)
if 0<jupiter_x<dim_x and 0<jupiter_y<dim_y:
    outstring += f",{jupiter.ra.deg:.5f},{jupiter.dec.deg:+.5f},{jupiter_x},{jupiter_y},{dist}"
else:
    outstring += f",,,,,{dist}"
print(outstring)
