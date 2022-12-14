import os, sys
import re
#import numpy as np
from h5py import File
FREQ="121-132"

imstack_file=sys.argv[1]
obsid = int(os.path.split(imstack_file)[1][:10])

with File(imstack_file, 'r') as imstack:
    #print(imstack_file)
    #print(obsid)
    group = imstack[FREQ]
    beam = group['beam']
    sigma =beam.attrs['SIGMA'].flatten() 
    scale=beam.attrs['SCALE'].flatten()
    print(f"{obsid},{sigma[0]},{sigma[1]},{scale[0]},{scale[1]}")
