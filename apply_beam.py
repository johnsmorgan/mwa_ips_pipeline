from optparse import OptionParser #NB zeus does not have argparse!
import numpy as np
from astropy.io import fits
import h5py

parser = OptionParser(usage = "usage:" +
    """
    python apply_beam.py \
               hdf5_file_in.h5py fitsfile_in.fits fitsfile_out.fits [-fr]
    """)
parser.add_option("-f", "--freq", default=None, dest="freq", help="freq")
parser.add_option("-r", "--reverse", action='store_true', dest="reverse", help="remove an already-applied primary beam correction")

opts, args = parser.parse_args()
hdf5_in= args[0]
fits_in= args[1]
fits_out= args[2]

if opts.freq is not None:
    group = opts.freq
else:
    group = '/'

df = h5py.File(hdf5_in, 'r')
beam = self.group['beam'][..., 0, 0] # last two dimensions are frequency and time
hdus = fits.open(fits_in)
in_data = hdus[0].data
n_x, n_y = in_data.shape[-1], in_data.shape[-2]
assert n_x == beam.shape[-3] and n_y == beam.shape[-4], "beam and image xy dimensions do not match"
if opts.reverse:
    out_data = in_data/np.average(1/beam, weights=beam**2, axis=0)**-1
else:
    out_data = in_data*np.average(1/beam, weights=beam**2, axis=0)**-1
hdus[0].data = out_data.reshape((1, 1, data_y, data_x)))
hdu.writeto(fits_out)
