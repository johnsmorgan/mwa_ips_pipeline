parser.add_argument('--beam_cutoff', default=0.1, help="beam cutoff (default: %(default)s)")
parser.add_argument('--beam', default='pbcor_norm', help="beam column (default: %(default)s)")
parser.add_argument('--complex', default='complex', help="Boolean column denoting 'complex' sources (default: %(default)s)")

bmaj, bmin, bpa = 60*header['BMAJ'], 60*header['BMIN'], header['BPA']
# select those sources with simple morphology
tabarray = table.as_array()
n = len(tabarray)
flagged = np.zeros(n, dtype=bool)
if 'complex' in tabarray.dtype.names:
    flagged = flagged | tabarray[args.complex]
    print(f"{np.sum(tabarray[args.complex])} complex, {np.sum(flagged)}/{n} flagged")

# classify by beam
low_beam = tabarray[args.beam] <= args.beam_cutoff
flagged = flagged | low_beam
print(f"{np.sum(low_beam)} lower than beam_cutoff ({args.beam_cutoff}), {np.sum(flagged)}/{n} flagged")

# poor fit
no_fit = tabarray[args.fit_col] == -1.0
flagged = flagged | no_fit
print(f"{np.sum(no_fit)} with no aegean fit, {np.sum(flagged)}/{n} flagged")

# Make new table with these flags applied
flagged_table = table[~flagged]
#flagged_table.write("flagged.vot", format='votable')

tab = flagged_table.as_array()

if np.mean(np.cos(Longitude(tab[args.ra_cat]*u.deg))) > 0:
    wrap_angle=180.*u.deg
else:
    wrap_angle=360.*u.deg

p = np.stack((Longitude(tab[args.ra_cat]*u.deg, wrap_angle=wrap_angle).deg,
              tab[args.dec_cat]), axis=-1)
q = np.stack((Longitude(tab[args.ra]*u.deg, wrap_angle=wrap_angle).deg,
              tab[args.dec]), axis=-1)
d = q-p

root, ext = os.path.splitext(args.outtable)
flagged_table[~outlier].write(args.outtable, format=args.out_format, overwrite=args.overwrite)
flagged_table[outlier].write(root+'_outliers'+ext, format=args.out_format, overwrite=args.overwrite)
