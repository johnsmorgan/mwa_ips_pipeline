#!/usr/bin/env python
import os
import numpy as np
from astropy.table import Table
from astropy.time import Time
from astropy.units import deg
from astropy.coordinates import SkyCoord, get_sun
from image_stack import ImageStack
from numpy import argsort, where, zeros, ones
from scipy.stats import norm

from optparse import OptionParser, OptionValueError

POL_OPTIONS=("XX", "YY", "I")

parser = OptionParser(usage = "usage: %prog input.hdf5 input.vot output.vot" +
"""

add various columns and delete unneeded ones.
""")
parser.add_option("-v", "--variability", dest="var", action="store_true", help="Calculate variability image parameters (dS etc)")
parser.add_option("-o", "--obsid", dest="obsid", default=None, help="time in gps format")
parser.add_option("--pol", dest="pol", default="I", help="primary beam polarisation to use: {} (default=%default)".format((", ".join(POL_OPTIONS))))

opts, args = parser.parse_args()
#FIXME add options for 
# freq
# ra column name
# dec column name
# new column name
# out table format
# variability
# gpstime
# set verbosity
if not opts.pol in POL_OPTIONS:
    raise OptionValueError, "polarisation must be one of %s" % (", ".join(POL_OPTIONS))
if os.path.exists(args[2]):
    os.remove(args[2])
imstack = ImageStack(args[0], freq='121-132')
t = Table.read(args[1])

# elongation
if not opts.obsid:
    opts.obsid = args[0][:10]
print "calculating elongations"
time = Time(float(opts.obsid), format='gps')
sun = get_sun(time.utc)
#t['elongation'] = sun.separation(SkyCoord(t['ra', 'dec']*deg))
t['elongation'] = sun.separation(SkyCoord(t['ra'], t['dec'], unit = "deg"))
t['snr'] = t['peak_flux'] / t['local_rms']

print "calculating primary beam"
t["pbcor"] = np.nan*ones(len(t))
# loop over all unmasked values
for s in np.argwhere(~t['ra'].mask)[:, 0]:
    print s,
    print imstack.world2pix(t['ra'][s], t['dec'][s])
    if opts.pol == "I":
        t["pbcor"][s] = imstack.world2beam(t['ra'][s], t['dec'][s], scale=False)
    elif opts.pol == "XX":
        t["pbcor"][s] = imstack.world2beam(t['ra'][s], t['dec'][s], avg_pol=False, scale=False)[0]
    elif opts.pol == "YY":
        t["pbcor"][s] = imstack.world2beam(t['ra'][s], t['dec'][s], avg_pol=False, scale=False)[1]

if opts.var:
    t['dS'] = np.sqrt((t['peak_flux']+t['background'])**2 - t['background']**2)
    t['err_dS'] = np.sqrt((t['peak_flux']+t['background']+t['local_rms'])**2 - t['background']**2) - t['dS']
    t['noise'] = np.sqrt((t['peak_flux']+t['background'])**2 - t['peak_flux']**2)
    t.keep_columns(['ra', 'err_ra', 'dec', 'err_dec', 'a', 'b', 'pa', 'elongation', 'pbcor', 'uuid', 'dS', 'err_dS', 'local_rms', 'noise', 'snr'])
else:
    t.keep_columns(['ra', 'err_ra', 'dec', 'err_dec', 'peak_flux', 'background', 'local_rms', 'a', 'b', 'pa', 'elongation', 'pbcor', 'uuid', 'snr'])

print "writing votable"
t.write(args[2], format='votable')
