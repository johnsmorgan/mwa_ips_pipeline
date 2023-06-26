#!/usr/bin/env python
import sys
import numpy as np
from astropy.io import fits
hdus = fits.open(sys.argv[1])
print(np.sum(np.isnan(hdus[0].data)))
