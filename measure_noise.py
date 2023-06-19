#!/usr/bin/env python
from h5py import File
import sys
import numpy as np
from astropy.io import fits
freq="121-132"
POLS = ('XX', 'YY')
obsid=sys.argv[1]
noise = []
for pol in POLS:
    hdus = fits.open(f"{obsid}_121-132image_moment2-{pol}.fits")
    noise.append(np.median(hdus[0].data))

with File("%s.hdf5" % obsid, 'r+') as imstack:
    group = imstack[freq]
    beam = group['beam']
    beam.attrs['SIGMA'] = np.array(noise)
    print(beam.attrs['SIGMA'])
