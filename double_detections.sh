#/bin/bash
stilts tmatch2 \
        in1=$1 \
        in2=$2 \
	icmd1="delcols 'elongation pbcor'"
        matcher=skyEllipse \
        values1="ra dec a b pa" \
        values2="ra dec a b pa" \
        suffix1="_cont" suffix2="_scint" \
	find="best2" \
        params=60 \
	fixcols='all' \
        ocmd='select snr_cont>5||snr_scint>5' \
	ocmd="colmeta -name elongation elongation_scint'"
	ocmd="colmeta -name pbcor pbcor_scint'"
	ocmd="addcol index dS/peak_flux_cont"
	ocmd="colmeta -desc 'Scintillation Index' index"
        out=$3

stilts tmatch2 \
        in1=$1 \
        in2=$2 \
        matcher=skyEllipse \
        values1="ra dec a b pa" \
        values2="ra dec a b pa" \
	find="best2" \
        params=60 \
	join=2not1 \
        out=$4 \
