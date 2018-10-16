#!/usr/bin/env bash
set -euo pipefail
# NB this script is not included in the makefile and must be run separately!

# take standard GLEAM catalogue and produce peak fluxes for IPS bands
# delete almost all columns

table_in=/data/catalogs/GLEAM.fits#2
table_out=gleam_ips_bands.fits
callingham_path=/data/catalogs/callingham2017
stilts tpipe \
	in=$table_in \
	out=$table_out \
	cmd='addcol Fp080 (Fp076*pow(e_Fp076,-2)+Fp084*pow(e_Fp084,-2))/(pow(e_Fp076,-2)+pow(e_Fp084,-2))' \
	cmd='addcol Fp162 (Fp158*pow(e_Fp158,-2)+Fp166*pow(e_Fp166,-2))/(pow(e_Fp158,-2)+pow(e_Fp166,-2))' \
	cmd='keepcols "GLEAM RAJ2000 DEJ2000 awide bwide pawide Fp080 Fp162 alpha e_alpha"'

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
