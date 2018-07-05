#!/bin/bash

# NB this script is not included in the makefile and must be included separately!

# Produce a catalogue of sources for ionospheric/absolute flux calibration
# With the following characteristics
# 1) bright -- in VLSS (or MRC for areas of the sky where that is unavailable)
# 2) good positions  -- in VLSS (or MRC for areas of the sky where that is unavailable)
# 3) isolated to reduce risk of bad crossmatch (no VLSS neighbour within 3 arcminutes)
# 
# Where possible GOOD GLEAM matches are given with flux densities to enable absolute flux calibration

table1=/data/catalogs/vlss_vizier.fits
table2=/data/catalogs/mrc.b64
table3=gleam_ips_bands.fits
table_out=ips_continuum_cal
stilts tcatn \
	nin=2 \
	in1=$table1 in2=$table2 \
	icmd1='keepcols "RAJ2000 DEJ2000"' \
	icmd2='keepcols "RA2000 DE2000"' \
	icmd1='select "DEJ2000>=-30&&(RAJ2000>=320||RAJ2000<=220||DEJ2000>=-10)"' \
	icmd2='select "DE2000<-30||(RA2000<320&&RA2000>220&&DE2000<-10)"' \
	out=$table_out

# remove all sources which have a match within 3 arcminutes
stilts tmatch1 \
	in=$table_out \
	matcher=sky \
	params=180 \
	values="RAJ2000 DEJ2000" \
	action=keep0 \
	out=$table_out

# Get GLEAM matches for absolute calibration purposes
stilts tmatch2 \
	in1=$table_out suffix1=""\
	in2=$table3 suffix2="_gleam" \
	matcher=sky \
	values1="RAJ2000 DEJ2000" \
	values2="RAJ2000 DEJ2000" \
	params=20 \
	join=all1 \
	ocmd="keepcols 'RAJ2000 DEJ2000 Fp080 Fp162 Separation'" \
	out=$table_out
