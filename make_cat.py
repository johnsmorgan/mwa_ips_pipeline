#!/usr/bin/env python
import os
import numpy as np
from astropy.table import Table
from astropy.time import Time
from astropy.coordinates import SkyCoord, get_sun
from imstack import ImageStack
from scipy.optimize import minimize


from optparse import OptionParser, OptionValueError

POL_OPTIONS=("XX", "YY", "I")

def get_ds(peak_flux, background, local_rms):
	"""
	dS from IPS Paper I equation
	"""
	dS = np.sqrt((peak_flux+background)**2 - background**2)
	err_dS = np.sqrt((peak_flux+background+local_rms)**2 - background**2) - dS
	return dS, err_dS

parser = OptionParser(usage = "usage: %prog input.hdf5 input.vot output.vot" +
"""

add various columns and delete unneeded ones.
""")
parser.add_option("-v", "--variability", dest="var", action="store_true", help="Calculate variability image parameters (dS etc)")
parser.add_option("-i", "--interp", dest="interp", action="store_true", help="Calculate interp image parameters (dS etc)")
parser.add_option("-o", "--obsid", dest="obsid", default=None, help="time in gps format used for calculation of Sun location (default: first 10 letters of input.hdf5)")
parser.add_option("--pol", dest="pol", default="I", help="primary beam polarisation to use: {} (default=%default)".format((", ".join(POL_OPTIONS))))
parser.add_option("-m", "--moment2", dest="moment2", action="store_true", help="Calculate variability image parameters (dS etc)")

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
if opts.var and opts.interp:
    raise OptionValueError("-v/--variability can not be set with -i/--interp")
if not opts.pol in POL_OPTIONS:
    raise OptionValueError("polarisation must be one of %s" % (", ".join(POL_OPTIONS)))
if os.path.exists(args[2]):
    os.remove(args[2])

imstack = ImageStack(args[0], freq='121-132')
dim_x, dim_y = imstack.group['beam'].shape[1:3]

t = Table.read(args[1])

# elongation
if not opts.obsid:
    opts.obsid = args[0][:10]
print("calculating elongations")
time = Time(float(opts.obsid), format='gps')
sun = get_sun(time.utc)
t['elongation'] = sun.separation(SkyCoord(t['ra'], t['dec'], unit = "deg"))

t['snr'] = t['peak_flux'] / t['local_rms']
if opts.interp:
    t['snr_scint'] = t['peak_flux2'] / t['local_rms2']

print("calculating primary beam max")
print(imstack.pix2beam(1200, 1200, scale=True))
f = lambda x: -imstack.pix2beam(np.int_(np.round(x[0])), np.int_(np.round(x[1])), scale=True)
min_ = minimize(fun=f, x0=(1200.0, 1200.0), method='Nelder-Mead', options={'xatol': 1})
pbmax = -min_['fun']

print("calculating primary beam for each source")
t["pbcor"] = np.nan*np.ones(len(t))
# loop over all unmasked values
for s in np.argwhere(~t['ra'].mask)[:, 0]:
    #print(s, sep=' ')
    x, y = imstack.world2pix(t['ra'][s], t['dec'][s])
    #print(x,y)
    if x<0 or x >= dim_x:
        continue
    if y<0 or y >= dim_y:
        continue
    if opts.pol == "I":
        t["pbcor"][s] = imstack.pix2beam(x, y, scale=True)
    elif opts.pol == "XX":
        t["pbcor"][s] = imstack.pix2beam(x, y, avg_pol=False, scale=True)[0]
    elif opts.pol == "YY":
        t["pbcor"][s] = imstack.pix2beam(x, y, avg_pol=False, scale=True)[1]
t["pbcor_norm"] = t["pbcor"]/pbmax

if opts.moment2:
    t['dS'], t['err_dS']= get_ds(t['peak_flux'], t['background'], t['local_rms'])
    t['scint_index'] = t['dS'] / t['peak_flux']
    t['err_scint_index'] = t['scint_index'] * t['err_dS'] / t['dS']
    t.keep_columns(['ra', 'err_ra', 'dec', 'err_dec', 'a', 'b', 'pa', 'elongation', 'pbcor', 'pbcor_norm', 'uuid', 'dS', 'err_dS', 'background', 'local_rms', 'snr'])
elif opts.interp:
    t['dS2'], t['err_dS2']= get_ds(t['peak_flux2'], t['background2'], t['local_rms2'])
    t['scint_index2'] = t['dS2'] / t['peak_flux2']
    t['err_scint_index2'] = t['scint_index2'] * t['err_dS2'] / t['dS2']
    t.keep_columns(['peak_flux', 'err_peak_flux', 'local_rms', 'snr', 'ra', 'err_ra', 'dec', 'err_dec', 'a', 'b', 'pa', 'elongation', 'pbcor', 'pbcor_norm', 'uuid', 'peak_flux2', 'background2', 'local_rms2', 'dS2', 'err_dS2', 'snr_scint', 'scint_index2', 'err_scint_index2'])
else:
    t.keep_columns(['ra', 'err_ra', 'dec', 'err_dec', 'a', 'b', 'pa', 'elongation', 'pbcor', 'pbcor_norm', 'uuid', 'peak_flux', 'background', 'local_rms', 'snr'])

print("writing votable")
t.write(args[2], format='votable')
