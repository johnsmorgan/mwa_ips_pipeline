#!/usr/bin/env python
import os
import numpy as np
from astropy.table import Table
from astropy.time import Time
from astropy.units import deg
from astropy.coordinates import SkyCoord, get_sun
from scint_parameters import get_solar_params

def time_to_sun_cartesian(t):
    """
    return sun ra, dec in radians
    """
    sun = get_sun(t)
    return sun.cartesian.xyz/sun.distance

N=1000
t = Table()

#time = Time(1234567890.+np.random.random(N)*365.25*86400, format='gps')
time = Time(1234567890., format='gps')
sun = get_sun(time)
t['ra'] = np.random.random(N)*360.
t['dec'] = np.random.random(N)*180. - 90
radec = SkyCoord(t['ra'], t['dec'], unit = "deg")
t['elongation1'] = sun.separation(radec)

sun_xyz = time_to_sun_cartesian(time)
sun_norm = np.sqrt(np.sum(sun_xyz**2))
print(sun_norm)
elongation, p, limb, sun_lat = get_solar_params(np.array(sun_xyz/sun_norm).reshape(3, 1), np.array(radec.cartesian.xyz))
t['elongation2'] = np.degrees(elongation)

print("writing votable")
t.write('out.vot', format='votable', overwrite=True)
