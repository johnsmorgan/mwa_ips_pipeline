# Tidy up continuum catalogue, rejecting anything within 5 degrees of the Sun
# FIXME sun exclusion doesn't work
stilts tmatch2 \
	in1=$1 \
	in2=$3 \
	out=$2 \
	ifmt2=csv \
	icmd1="addcol snr peak_flux/local_rms" \
	icmd1='sort -down snr' \
	icmd1='keepcols "ra dec a b pa peak_flux local_rms snr uuid"' \
	matcher=sky \
	params=36000 \
	values1="ra dec" \
	values2="RAJ2000 DEJ2000" \
	join=1not2

