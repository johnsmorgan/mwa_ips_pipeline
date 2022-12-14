#!/usr/bin/env python
"""
Take grouped catalogue and identify those sources that meet
the criteria for inclusion in the catalogue
"""
import argparse
import sys
import os
import numpy as np
from astropy.table import Table, Column
import logging

logging.basicConfig(format='%(asctime)s-%(levelname)s %(message)s', level=logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument('intable', help='Input table')
parser.add_argument('outtable', help='Output table')
parser.add_argument('--source', default='Source_name_tgss', help='column name containing source ID')
parser.add_argument('--pb', default='pbcor_norm', help='column name pb value')
parser.add_argument('--pbthresh', default=0.5, help='pb threshold')
args = parser.parse_args()

if os.path.exists(args.outtable):
    os.remove(args.outtable)
logging.debug("reading input")

intable = Table.read(args.intable)

# remove integer column or fill won't work
t = intable.as_array()

# find indices of unique TGSS sources
_, tgss_unique = np.unique(t[args.source], return_index=True)

outtable = intable[tgss_unique]
t1 = outtable.as_array()
n = len(t1)
logging.info("%d unique sources from %d measurements", n, len(t))
selected = np.zeros(n, dtype=bool)
n_group = np.zeros(n, dtype=int)

for s, source in enumerate(t1[args.source]):
    #logging.info("processing source %d of %d", s+1, n)
    group = t[args.source] == source
    n_group[s] = np.sum(group)
    t_group = t[group]
    idx_max = np.argmax(t_group['pbcor_norm'])
    if t_group[idx_max]['pbcor_norm'] > args.pbthresh:
        selected[s] = True
    if t_group[idx_max]['name_match2'] == source:
        logging.warning('name_match2 matches')
    for col in ('obsid', 'RA_tgss', 'DEC_tgss', 'ra', 'dec', 'ra_corr', 'dec_corr', 'Source_name_tgss', 'p_match1', 'p_match2', 'name_match2', 'elongation', 'GLEAM', 'Fp162', 'pbcor_norm', 'snr', 'sigma_ips_tgss', 'SepArcM_tgss', 'Separation_tgss', 'SepArcM_gleam', 'Separation_gleam'):
        outtable[s][col] = t_group[idx_max][col]
outtable['selected'] = selected
outtable['n'] = n_group

outtable.write(args.outtable, format='votable')
