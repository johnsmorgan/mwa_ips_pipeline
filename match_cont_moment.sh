#!/usr/bin/env bash
set -euo pipefail
topcat -stilts tmatch2 \
        in1=$1 \
        in2=$2 \
	params=60 \
	matcher=sky \
        values1='ra_corr dec_corr' \
        values2='ra_corr dec_corr' \
	suffix1="_cont" \
	suffix2="_mom2" \
        out=$3
