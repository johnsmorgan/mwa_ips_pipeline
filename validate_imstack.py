import sys, os
from zlib import adler32
from h5py import File
import numpy as np

FREQ="121-132"

size = os.path.getsize(sys.argv[1])

df = File(sys.argv[1], 'r')
group = df['121-132']
assert 'continuum' in group.keys(), "can't find continuum"
#assert group['continuum'].shape == (2, 2400, 2400, 1, 1), "unexpected continuum shape" % group['continuum'].shape

trace = df['121-132']['image'][:, 1200, 1200, 0, :]
beam = 'beam' in df['121-132']
nan = np.sum(~np.isfinite(trace))
zero = np.sum(trace==0.0)
adler = np.base_repr(adler32(trace[0]), 16).zfill(8) + np.base_repr(adler32(trace[1]), 16).zfill(8)
print(f"{size},{nan},{zero},{adler}")
