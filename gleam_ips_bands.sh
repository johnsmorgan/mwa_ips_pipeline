# NB this script is not included in the makefile and must be run separately!

# take standard GLEAM catalogue and produce peak fluxes for IPS bands
# delete almost all columns

#table_in=/data/catalogs/GLEAM.fits#2
#table_out=gleam_ips_bands.fits
#stilts tpipe \
#	in=$table_in \
#	out=$table_out \
#	cmd='addcol Fp080 (Fp076*pow(e_Fp076,-2)+Fp084*pow(e_Fp084,-2))/(pow(e_Fp076,-2)+pow(e_Fp084,-2))' \
#	cmd='addcol Fp162 (Fp158*pow(e_Fp158,-2)+Fp166*pow(e_Fp166,-2))/(pow(e_Fp158,-2)+pow(e_Fp166,-2))' \
#	cmd='keepcols "GLEAM RAJ2000 DEJ2000 awide bwide pawide Fp080 Fp162"'

stilts tmatch2 \
	in1=$table_out \
	in2=high_low_freq_peakedspectrum_table.fits \
	out=$table_out \
	icmd2="keepcols Gleam_name nu_p nu_p_error" \
	matcher=ExactValue\
	values1="GLEAM" \
	values2="Gleam_name" \

stilts tmatch2 \
	in1=$table_out \
	in2=gps_sample_peakedspectrum_table.fits \
	out=$table_out \
	icmd2="keepcols Gleam_name" \
	matcher=ExactValue\
	values1="GLEAM" \
	values2="Gleam_name" \
	ocmd="addcol gps !NULL_Gleam_name" \
	ocmd="delcols Gleam_name"

stilts tmatch2 \
	in1=$table_out \
	in2=srcs_peak_below72MHz.fits \
	out=$table_out \
	icmd2="keepcols Gleam_name" \
	matcher=ExactValue\
	values1="GLEAM" \
	values2="Gleam_name" \
	ocmd="addcol peak_below_72mhz !NULL_Gleam_name" \
	ocmd="delcols Gleam_name"

stilts tmatch2 \
	in1=$table_out \
	in2=convex_src_table.fits \
	out=$table_out \
	icmd2="keepcols Gleam_name" \
	matcher=ExactValue\
	values1="GLEAM" \
	values2="Gleam_name" \
	ocmd="addcol convex !NULL_Gleam_name" \
	ocmd="delcols Gleam_name"
