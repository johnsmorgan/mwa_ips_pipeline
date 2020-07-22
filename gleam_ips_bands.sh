#!/usr/bin/env bash
set -xeuo pipefail
# NB this script is not included in the makefile and must be run separately!

# take standard GLEAM catalogue and produce peak fluxes for IPS bands
# delete almost all columns

table_in=/data/catalogs/GLEAM.fits#2
table_in_gal=/data/catalogs/gleam2.fits
table_out=gleam_ips_bands.fits
callingham_path=/data/catalogs/callingham2017

stilts tcat \
	in=$table_in \
	in=$table_in_gal \
	out=$table_out \
	icmd='keepcols "GLEAM RAJ2000 DEJ2000 awide bwide pawide Fp076 e_Fp076 Fp084 e_Fp084 Fp158 e_Fp158 Fp166 e_Fp166 alpha e_alpha"' \
	seqcol='galactic' \
	ocmd='replacecol galactic galactic==2' \
	ocmd='addcol Fp080 (Fp076*pow(e_Fp076,-2)+Fp084*pow(e_Fp084,-2))/(pow(e_Fp076,-2)+pow(e_Fp084,-2))' \
	ocmd='addcol Fp162 (Fp158*pow(e_Fp158,-2)+Fp166*pow(e_Fp166,-2))/(pow(e_Fp158,-2)+pow(e_Fp166,-2))' \
	ocmd='keepcols "GLEAM RAJ2000 DEJ2000 awide bwide pawide Fp080 Fp162 alpha e_alpha galactic"'

stilts tmatch2 \
	in1=$table_out \
	in2=$callingham_path/high_low_freq_peakedspectrum_table.fits \
	out=$table_out \
	join=all1 \
	icmd2='keepcols "Gleam_name nu_p nu_p_error"' \
	icmd2="replacecol Gleam_name substring(Gleam_name,6)" \
	matcher=exact\
	values1="GLEAM" \
	values2="Gleam_name" \
	ocmd="delcols Gleam_name"

stilts tmatch2 \
	in1=$table_out \
	in2=$callingham_path/gps_sample_peakedspectrum_table.fits \
	out=$table_out \
	join=all1 \
	icmd2="keepcols Gleam_name" \
	icmd2="replacecol Gleam_name substring(Gleam_name,6)" \
	matcher=exact\
	values1="GLEAM" \
	values2="Gleam_name" \
	ocmd="addcol gps !NULL_Gleam_name" \
	ocmd="delcols Gleam_name"

stilts tmatch2 \
	in1=$table_out \
	in2=$callingham_path/srcs_peak_below72MHz.fits \
	out=$table_out \
	join=all1 \
	icmd2="keepcols Gleam_name" \
	icmd2="replacecol Gleam_name substring(Gleam_name,6)" \
	matcher=exact\
	values1="GLEAM" \
	values2="Gleam_name" \
	ocmd="addcol peak_below_72mhz !NULL_Gleam_name" \
	ocmd="delcols Gleam_name"

stilts tmatch2 \
	in1=$table_out \
	in2=$callingham_path/convex_src_table.fits \
	out=$table_out \
	join=all1 \
	icmd2="keepcols Gleam_name" \
	icmd2="replacecol Gleam_name substring(Gleam_name,6)" \
	matcher=exact\
	values1="GLEAM" \
	values2="Gleam_name" \
	ocmd="addcol convex !NULL_Gleam_name" \
	ocmd="delcols Gleam_name"
