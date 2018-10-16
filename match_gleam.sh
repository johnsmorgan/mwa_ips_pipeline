#!/usr/bin/env bash
set -euo pipefail
master=$3/gleam_ips_bands.fits
stilts tmatch2 \
        in1=$1 \
        in2=$master \
	icmd2="addcol flat NULL_alpha?Fp162>(Fp080*sqrt(2)):alpha>-0.5" \
	icmd2="addcol peaked !NULL_nu_p" \
	icmd2="keepcols 'GLEAM RAJ2000 DEJ2000 awide bwide pawide Fp162 peaked gps peak_below_72mhz convex flat'" \
        matcher=SkyEllipse \
	params=60 \
        values1='ra_corr dec_corr a b pa' \
        values2='RAJ2000 DEJ2000 awide bwide pawide' \
	suffix1="" \
	suffix2="_gleam" \
	find=best1 \
	join=all1 \
	ocmd="colmeta -name Separation_gleam Separation" \
	ocmd="addcol SepArcM_gleam 60*skyDistanceDegrees(RAJ2000,DEJ2000,ra_corr,dec_corr)" \
        out=$2
