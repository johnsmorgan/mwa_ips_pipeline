#!/usr/bin/env bash
set -euo pipefail

topcat -stilts tmatch2 \
        in1=$1 \
        in2=$2 \
	icmd2="select pbcor_norm>0.25" \
	matcher=SkyEllipse \
	params=60 \
	values1="RAJ2000 DEJ2000 awide bwide pawide" \
	values2="ra_corr dec_corr 0 0 0" \
	join=2not1 \
	suffix1="" \
	suffix2="" \
	find=best \
	out=$3
