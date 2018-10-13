#/bin/bash
stilts tmatch2 \
        in1=$1 \
        in2=$2 \
        matcher=skyEllipse \
        values1="ra dec a b pa" \
        values2="ra dec a b pa" \
        suffix1="_cont" suffix2="_scint" \
	find="best2" \
        params=60 \
        out=$3 \
        # ocmd='select snr_cont>5||snr_scint>5' \

