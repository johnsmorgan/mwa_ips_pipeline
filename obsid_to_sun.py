"""
write out sun coordinates for a given obsid to a single-line .csv file
"""
import sys
from astropy.time import Time
from astropy.coordinates import get_sun

obsid = sys.argv[1]
time = Time(float(obsid), format='gps')
sun = get_sun(time.utc)
f = open("%s_sun.csv" % obsid, 'w')
print >> f, "RAJ2000,DEJ2000"
print >> f, "%f,%f" % (sun.ra.deg, sun.dec.deg)
