import numpy as np

from scipy.constants import c

# North pole of rotational axis of Sun in J2000.0

SUN_POLE_RA =  286.13 # degrees
SUN_POLE_DEC = +63.87 # degrees
# or equivalently,
SUN_POLE_XYZ = np.array([ 0.12235349,-0.42307208, 0.8977971 ])

def dot_array(a, b, axis=0):
    """
    assume array is a list of vectors along axis
    dot one vector with other 
    """
    return np.sum(a*b, axis=axis)

##########################
# Scintillation parameters
##########################

# apart from the constants from scipy, the following functions rely only on numpy

def get_wavelength(freq_mhz):
    return c/(freq_mhz*1e6)

def get_scint_index(p, phi, wavelength, cutoff=0.7, rho=1.0, b=1.6):
    """
    Calculate IPS scintillation index based on wavelength and solar elongation (radians)
    See e.g. Rickett (1973)
    phi in radians
    p (approx au)
    """
    e_factor = np.hypot(np.cos(phi), rho*np.sin(phi))
    m = 0.06*wavelength*(e_factor*p)**-b
    return np.where(m<cutoff, m, cutoff)

def get_scint_index_eq(p, phi, wavelength, cutoff=0.7, phi_cutoff=30, b=1.6):
    """
    Calculate IPS scintillation index based on wavelength and solar elongation (radians)
    See e.g. Rickett (1973)
    phi in radians
    p (approx au)
    """
    m = np.where(np.abs(phi)<np.radians(phi_cutoff), 0.06*wavelength*p**-b, 0.0)
    return np.where(m<cutoff, m, cutoff)

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
    return np.where(m < cutoff2, np.where(m<cutoff1, m, cutoff1), 0)

def get_fresnel_size(distance, wavelength):
    """
    distance/M, wavelength/M
    apparent size of fresnel length (arcsec)
    """
    return 3600*np.degrees(np.sqrt(wavelength/(2*np.pi*distance)))

def get_solar_params(sun, target, long_elong=72.):
    """
    calculate parameters of line of sight to target relative to Sun rotation axis 

    Parameters 
    ----------

    Location of Sun in sky as unit cartesian vector (RAJ2000)
    Location of target in sky as unit cartesian vector (RAJ2000)

    Returns 
    -------
    elongation (radians)
    limb ('E' or 'W')
    solar latitude below pierce point (if elongation<90, else None)
    """
    ce = dot_array(sun, target)
    elongation = np.arccos(ce)

    # get limb
    east_vector = np.cross(SUN_POLE_XYZ, np.squeeze(sun)).reshape(3, 1)
    east_vector /= np.sqrt(np.sum(east_vector**2)) #normalise
    limb = np.where(dot_array(east_vector, target) > 0, 'E', 'W')

    #earth_screen = np.where(elongation < np.radians(long_elong), ce*target, 0.3*target)
    earth_screen = ce*target
    sun_screen = earth_screen-sun
    p = np.sqrt(np.sum(sun_screen**2, axis=0))
    sun_screen /= p
    sun_lat = np.pi/2 - np.arccos(dot_array(sun_screen, SUN_POLE_XYZ.reshape(3, 1)))
    return elongation, p, limb, sun_lat
