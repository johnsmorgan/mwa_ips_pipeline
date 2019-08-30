import os
import numpy as np
from astropy.table import Table
from matplotlib import pyplot as plt
from optparse import OptionParser

COLORS = (
'#000000',
'#0072b2',
'#56b4e9',
'#009e73',
'#cc79a7',
'#d55e00',
'#e69f00',
'#f0e442')
OBSID=1147217904
FREQ='121-132'
WAVELENGTH=1.85

def m_weak(p, l):
    """
    predict scint index given p and wavelength
    """
    m = 0.06*l*p**-1.6
    return np.where(m<1, m, 1.0)


parser = OptionParser(usage = "usage: %prog input.vot output.png" +
"""
Plot m-p curve
""")
opts, args = parser.parse_args()

if os.path.exists(args[1]):
    os.remove(args[1])

t = Table.read(args[0])

fig = plt.figure(figsize=(16, 12))
normal = ~(t['peaked'] | t['flat'])
flat = (t['flat'] & ~(t['peaked'] | t['gps'] | t['peak_below_72mhz'] | t['convex']))
plt.errorbar(np.sin(np.radians(t['elongation'])), t['scint_index'], t['index_err'], fmt=',', capsize=0, color=COLORS[0], label='_nolegend_')
plt.plot(np.sin(np.radians(t['elongation'][normal])), t['scint_index'][normal], '+', markersize=8, color='black', label='_nolegend_')
plt.plot(np.sin(np.radians(t['elongation'][flat])), t['scint_index'][flat], 'o', markersize=8, alpha=0.75, color='black', markerfacecolor='none', label='flat')
plt.plot(np.sin(np.radians(t['elongation'][t['gps']])), t['scint_index'][t['gps']], 'o', markersize=8, alpha=0.75, color=COLORS[2], label='gps')
plt.plot(np.sin(np.radians(t['elongation'][t['peaked']])), t['scint_index'][t['peaked']], 'o', markersize=10, alpha=0.75, color=COLORS[3], label='gleam pk')
plt.plot(np.sin(np.radians(t['elongation'][t['peak_below_72mhz']])), t['scint_index'][t['peak_below_72mhz']], 'o', markersize=8, alpha=0.75, color=COLORS[4], label='pk<72')
plt.plot(np.linspace(0.01, 1, 100), m_weak(np.linspace(0.01, 1, 100), WAVELENGTH), linestyle='--', color='grey')
plt.xlim(0.0, 1)
plt.ylim(0, 1)
plt.xlabel('$p$ / AU')
plt.ylabel('$m$')
plt.legend(loc='lower left', numpoints=1)
plt.savefig(args[1])
plt.close()
