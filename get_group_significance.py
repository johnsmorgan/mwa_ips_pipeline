import os
from astropy.table import Table
from numpy import argsort, where, zeros, ones
from scipy.stats import norm

from optparse import OptionParser

parser = OptionParser(usage = "usage: %prog input1.vot input2.vot output.vot" +
"""
Add three further columns to input 2 with name of best match, name of first alternative match, and probabilities of each.

input2 should contain one row per source
input1 should contain multipe rows per source, one for each potential match, with these linked with the 'GroupID' column.

Prints out lots of useful information.
""")

# FIXME lots of hard-coded stuff here that should be user-settable.
opts, args = parser.parse_args()

if os.path.exists(args[2]):
    os.remove(args[2])

FREQ='118-129'
OFFSET = 0.347
CAT='tgss'
SNR_THRESH = 0.0
MATCH_THRESH = 2.0*OFFSET

t = Table.read(args[0])
t['p'] = where(t['sigma_ips_%s' % CAT] > SNR_THRESH, ones(len(t)), zeros(len(t)))
t2 = Table.read(args[1])
# add new columns to t2
t2["p_match1"] = ones(len(t2))
t2["name_match2"] = Table.MaskedColumn([""]*len(t2), mask=[True]*len(t2), dtype='S24')
t2["p_match2"] = zeros(len(t2))
n_suspicious = 0
n_undetected = 0
hi_lr = 0
lo_snr = 0
n_100 =0
n_99 = 0
n_95 = 0
n_nomatch = 0
for g in range(t['GroupID'].min(), t['GroupID'].max()):
    #group_gt_thresh = (t['GroupID'] == g) & (t['sigma_ips_%s' % CAT] > SNR_THRESH)
    group_gt_thresh = (t['GroupID'] == g)
    seps =  t[group_gt_thresh]['SepArcM_%s' % CAT]
    source_names = t[group_gt_thresh]['Source_name_%s' % CAT]
    if len(seps) < 2:
        if len(seps) == 0:
            n_nomatch += 1
        print(t2[t2['GroupID'] == g]['GroupID'])
        t2['GroupID'][t2['GroupID'] == g] = -g
        continue
    n_100 += 1
    likelihoods = norm.pdf(seps/OFFSET)
    likelihoods /= sum(likelihoods)
    t['p'][group_gt_thresh] = likelihoods
    idx = argsort(seps)
    t2['p_match1'][t2['GroupID'] == g] = likelihoods[idx][0]
    t2['name_match2'][t2['GroupID'] == g] = source_names[idx][1]
    t2['p_match2'][t2['GroupID'] == g] = likelihoods[idx][1]
    if likelihoods[idx][0] < 0.99:
        n_99 += 1
        print('*', sep='', end='')
    if likelihoods[idx][0] < 0.95:
        n_95 += 1
        print('*', sep='', end='')
    else:
        t2['GroupID'][t2['GroupID'] == g] = -g
    print()
    
    mini_table = t[group_gt_thresh]['sigma_ips_%s' % CAT, 'SepArcM_%s' % CAT, 'p']
    mini_table['p'].format = '%1.3g'
    mini_table['SepArcM_%s' % CAT].format = '%1.2g'
    mini_table['sigma_ips_%s' % CAT].format = '%4.1f'

    idx_tab = argsort(mini_table['SepArcM_%s' % CAT])
    print("group %d" % g)
    print(mini_table[idx_tab])
    print()
print("ngroups = %d" % g)
print("nnomatch = %d" % n_nomatch)
print("n100 = %d" % n_100)
print("n99 = %d" % n_99)
print("n95 = %d" % n_95)
t2.write(args[2], format='votable')
