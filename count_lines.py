#!/usr/bin/env python
import sys
import numpy as np
from astropy.table import Table
tab = Table.read(sys.argv[1])
print(len(tab))
