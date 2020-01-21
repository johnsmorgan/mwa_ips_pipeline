"""
Write out sun coordinates for a given obsid to a single-line .csv file
"""
from astropy.time import Time
from astropy.coordinates import get_sun, SkyCoord
from optparse import OptionParser

parser = OptionParser(usage = "usage: %prog obsid" +
"""
Produces a .csv file containing the coordinates of the Sun at the given GPS time
""")
parser.add_option("--ecliptic", dest="ecliptic", action="store_true", help="Give Sun coordinates in ecliptic rather than the default J2000 equatorial")
opts, args = parser.parse_args()
if not len(args) is 1:
    parser.error("wrong number of arguments")

obsid = args[0]
time = Time(float(obsid), format='gps')
sun = get_sun(time.utc)
with open("%s_sun.csv" % obsid, 'w') as f:
    if not opts.ecliptic:
        print >> f, "RAJ2000,DEJ2000"
        print >> f, "%f,%f" % (sun.ra.deg, sun.dec.deg)
    else:
        sun2 = SkyCoord(sun.ra, sun.dec).geocentrictrueecliptic
        print >> f, "LON,LAT"
        print >> f, "%f,%f" % (sun2.lon.deg, sun2.lat.deg)

