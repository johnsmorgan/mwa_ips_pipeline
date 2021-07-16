#!/usr/bin/env bash
exit 0
set -euo pipefail
topcat -stilts tmatch2 \
        in1=$1 \
        in2=$2 \
	icmd1='delcols "elongation pbcor"' \
        matcher=skyEllipse \
        values1="ra dec a b pa" \
        values2="ra dec a b pa" \
        suffix1="_cont" suffix2="_scint" \
	find="best2" \
        params=60 \
        ocmd='select snr_cont>5||snr_scint>5' \
	ocmd="colmeta -name peak_flux_cont peak_flux" \
	ocmd="addcol scint_index dS/peak_flux_cont" \
	ocmd='colmeta -desc "Scintillation Index" scint_index' \
	ocmd="addcol index_err scint_index*hypot(err_dS/dS,local_rms_cont/peak_flux_cont)" \
        out=$3

	#ocmd="colmeta -name background_cont background" \

stilts tmatch2 \
        in1=$1 \
        in2=$2 \
        matcher=skyEllipse \
        values1="ra dec a b pa" \
        values2="ra dec a b pa" \
	find="best2" \
        params=60 \
	join=2not1 \
        out=$4
