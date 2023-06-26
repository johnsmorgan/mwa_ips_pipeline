#!/usr/bin/env bash
set -euo pipefail
# $1 should be infield catalogue
# $2 should be continuum catalogue
# $3 should be moment2 catalogue
# $4 should be output catalogue
# $5 RA column of master catalogue
# $6 DEC column of master catalogue

topcat -stilts tmatch2 \
        in1=$1 \
        in2=$2 \
	icmd2='keepcols "ra_corr dec_corr a b pa uuid elongation peak_flux local_rms snr snr_scint dS2 err_dS2 peak_flux2 local_rms2"' \
	matcher=SkyEllipse \
	params=60 \
	values1="${5:-RA_tgss} ${6:-DEC_tgss} 0 0 0" \
	values2="ra_corr dec_corr a b pa" \
	join=all1 \
	suffix1="" \
	suffix2="" \
	find=best \
	out=tmp.vot

topcat -stilts tmatch2 \
        in1=tmp.vot \
        in2=$3 \
	icmd2='keepcols "ra_corr dec_corr dS err_dS a b pa uuid snr"' \
	matcher=SkyEllipse \
	params=60 \
	values1="${5:-RA_tgss} ${6:-DEC_tgss} 0 0 0" \
	values2="ra_corr dec_corr a b pa" \
	join=all1 \
	suffix1="" \
	suffix2="_moment2" \
	find=best \
	fixcols='all' \
	out=$4
rm tmp.vot
