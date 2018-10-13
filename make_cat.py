#!/usr/bin/env python
from astropy.table import Table
from astropy.time import Time
from astropy.units import deg
from astropy.coordinates import get_sun
from image_stack import ImageStack
from numpy import argsort, where, zeros, ones
from scipy.stats import norm

from optparse import OptionParser

parser = OptionParser(usage = "usage: %prog input.hdf5 input.vot output.vot" +
"""

add various columns and delete unneeded ones.
""")

opts, args = parser.parse_args()
parser.add_option("-v", "--variability", dest="var", action="store_true", help="Calculate variability image parameters (dS etc)")
#FIXME add options for 
# freq
# ra column name
# dec column name
# new column name
# out table format
# variability
# gpstime

imstack = ImageStack(args[0], freq='121-132')

# elongation
obsid = float(args[0][:10])
time = Time(obsid, format='gps')
sun = get_sun(time.utc)
t['elongation'] = sun.separation(SkyCoord(t['ra', 'dec']*deg))

t = Table.read(args[1])
t["pbcor"] = ones(len(t))
for s in range(len(t)):
    t["pbcor"][s] = imstack.get_beam(t['ra'][s], t['dec'][s])
    t["elongation"][s] = sun.separation(t['ra'][s], t['dec'][s])

if opts.var:
    t['dS'] = (t['peak_flux']+t['background'])**2 - t['background']**2
    t['err_dS'] = (t['peak_flux']+t['background']+t['local_rms'])**2 - t['background']**2 - t['dS']
    t['noise'] = (t['peak_flux']+t['background'])**2 - t['peak_flux']**2
    t.keep_columns(['ra', 'err_ra', 'dec', 'err_dec',  'dS', 'err_dS', 'noise', 'a', 'b', 'pa', 'uuid'])
else:
    t.keep_columns(['ra', 'err_ra', 'dec', 'err_dec',  'peak_flux', 'background', 'local_rms', 'a', 'b', 'pa', 'uuid'])

t.write(args[2], format='votable')
