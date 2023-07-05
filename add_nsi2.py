#!/usr/bin/env python
import os
import logging
import numpy as np
from astropy.table import Table
from astropy.time import Time
from astropy.units import deg
from astropy.coordinates import SkyCoord, get_sun
from scint_parameters import get_solar_params
from imstack import ImageStack

from optparse import OptionParser, OptionValueError

POL_OPTIONS=("XX", "YY", "I")
WAVELENGTH=1.862
RA_COL='ra'
DEC_COL='ra'

def time_to_sun_cartesian(t):
    """
    return sun ra, dec in radians
    """
    sun = get_sun(t)
    return sun.cartesian.xyz/sun.distance

def get_scint_index2(p, phi, wavelength, cutoff1=0.8, cutoff2=2.0, rho=1.0, b=1.6):
    """
    Calculate IPS scintillation index based on wavelength and solar elongation (radians)
    See e.g. Rickett (1973)
    phi in radians
    p (approx au)
    cutoff1 - outer cutoff, this is the maximum scintillation index
    cutoff2 - inner cutoff, at higher scintillation indices, no detection possible
    """
    e_factor = np.hypot(np.cos(phi), rho*np.sin(phi))
    m = 0.06*wavelength*(e_factor*p)**-b
    return np.where(m < cutoff2, np.where(m<cutoff1, m, cutoff1), np.nan)

parser = OptionParser(usage = "usage: %prog input.vot output.vot" +
"""

add various columns and delete unneeded ones.
""")
parser.add_option("-o", "--obsid", dest="obsid", default=None, help="time in gps format used for calculation of Sun location (default: first 10 letters of input.hdf5)")
parser.add_option("--ra_col", dest="ra_col", default=RA_COL, help="RA column")
parser.add_option("--dec_col", dest="dec_col", default=DEC_COL, help="Decl. column")
parser.add_option("-v", "--verbose", action="count", dest="verbose", default=0, help="-v info, -vv debug")

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
if opts.verbose == 0:
    logging.basicConfig(format='%(asctime)s-%(levelname)s %(message)s', level=logging.WARNING)
elif opts.verbose == 1:
    logging.basicConfig(format='%(asctime)s-%(levelname)s %(message)s', level=logging.INFO)
else:
    logging.basicConfig(format='%(asctime)s-%(levelname)s %(message)s', level=logging.DEBUG)

if os.path.exists(args[1]):
    os.remove(args[1])

t = Table.read(args[0])

# elongation
if not opts.obsid:
    opts.obsid = args[0][:10]
logging.info("calculating elongations")
time = Time(float(opts.obsid), format='gps')
sun = get_sun(time.utc)
#t['elongation'] = sun.separation(SkyCoord(t['ra', 'dec']*deg))
radec = SkyCoord(t[opts.ra_col], t[opts.dec_col], unit = "deg")
#t['elongation'] = sun.separation(radec)
#t['snr'] = t['peak_flux'] / t['local_rms']

sun_xyz = time_to_sun_cartesian(time)
elongation, p, limb, sun_lat = get_solar_params(np.array(sun_xyz).reshape(3, 1), np.array(radec.cartesian.xyz))
logging.debug("elongations: %s", elongation)
logging.debug("limb: %s", limb)
t['elongation2'] = np.degrees(elongation)
#t['p'] = p
t['limb'] = limb
t['sun_lat'] = np.degrees(sun_lat)
m1 = get_scint_index2(p, np.radians(t['sun_lat']), WAVELENGTH, cutoff1=1.0, cutoff2=1.0, rho=1.0, b=1.6)
m2 = get_scint_index2(p, np.radians(t['sun_lat']), WAVELENGTH, cutoff1=1.0, cutoff2=1.0, rho=1.5, b=1.6)
t['mpt1'] = m1
t['mpt2'] = m2
#t['nsi1'] = t['scint_index']/m1
#t['nsi2'] = t['scint_index']/m2
#t['e_nsi1'] = t['err_scint_index']/m1
#t['e_nsi2'] = t['err_scint_index']/m2

logging.info("writing votable")
t.write(args[1], format='votable')
