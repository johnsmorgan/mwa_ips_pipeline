# NB this script is not included in the makefile and must be run separately!

# take standard GLEAM catalogue and produce peak fluxes for IPS bands
# delete almost all columns

table_in=/data/catalogs/GLEAM.fits#2
table_out=gleam_ips_bands.fits
stilts tpipe \
	in=$table_in \
	out=$table_out \
	cmd='addcol Fp080 (Fp076*pow(e_Fp076,-2)+Fp084*pow(e_Fp084,-2))/(pow(e_Fp076,-2)+pow(e_Fp084,-2))' \
	cmd='addcol Fp162 (Fp158*pow(e_Fp158,-2)+Fp166*pow(e_Fp166,-2))/(pow(e_Fp158,-2)+pow(e_Fp166,-2))' \
	cmd='keepcols "GLEAM RAJ2000 DEJ2000 awide bwide pawide Fp080 Fp162"'

