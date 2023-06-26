import os
from optparse import OptionParser
import numpy as np
from astropy.io import fits
import h5py

HDF5_OUT = "%s_beam.hdf5"
VERSION='0.1'
POLS=['XX', 'YY']

parser = OptionParser(usage = "usage:" +
    """
        python make_beam_only.py \
               my_hdf5_file.hdf5 my_hdf5_file_out.hdf5""")
parser.add_option("-f", "--freq", default=None, dest="freq", help="freq")

opts, args = parser.parse_args()
hdf5_in_path= args[0]
hdf5_out_path= args[1]

assert not os.path.exists(hdf5_out_path), "out path already exists!"

if opts.freq is not None:
    group = opts.freq
else:
    group = '/'

with h5py.File(hdf5_in_path, 'r') as hdf5_in:
    with h5py.File(hdf5_out_path, 'w') as hdf5_out:
        hdf5_out.attrs['VERSION'] = VERSION
        if opts.freq is not None:
            hdf5_out.create_group(group)
        else:
            group="/"
        hdf5_in.copy(hdf5_in[group]['beam'], hdf5_out[group])
        hdf5_in.copy(hdf5_in[group]['header'], hdf5_out[group])
