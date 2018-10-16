#!/usr/bin/env bash
set -euo pipefail
master=$2/TGSSADR1_7sigma_catalog.fits

stilts tmatch2 \
        in1=$1 \
        in2=$master \
	icmd2="keepcols 'Source_name RA DEC Maj Min PA Peak_flux E_Peak_flux Source_code'" \
	icmd2="replacecol Peak_flux Peak_flux/1000" \
	icmd2="replacecol E_Peak_flux E_Peak_flux/1000" \
	icmd2="colmeta -unit 'beam-1 Jy' Peak_flux" \
	icmd2="colmeta -unit 'beam-1 Jy' E_Peak_flux" \
	matcher=SkyEllipse \
	params=60 \
	values1='ra_corr dec_corr a b pa' \
	values2='RA DEC Maj Min PA' \
	suffix1="" \
	suffix2="_tgss" \
	find=all \
	fixcols='all' \
	ocmd="addcol SepArcM_tgss 60*skyDistanceDegrees(RA_tgss,DEC_tgss,ra_corr,dec_corr)" \
	ocmd="addcol sigma_ips_tgss (hypot(Peak_flux_tgss,noise/pbcor)-noise/pbcor)/(local_rms/pbcor)" \
	ocmd="colmeta -desc 'S/N tgss would have scintillating at 100% in variability image' sigma_ips_tgss" \
	ocmd="colmeta -name Separation_tgss Separation" \
	out=${1%.vot}_all.vot

stilts tmatch2 \
	in1=$1 \
	in2=$master \
	icmd2="keepcols 'Source_name RA DEC Maj Min PA Peak_flux E_Peak_flux Source_code'" \
	icmd2="replacecol Peak_flux Peak_flux/1000" \
	icmd2="replacecol E_Peak_flux E_Peak_flux/1000" \
	icmd2="colmeta -unit 'beam-1 Jy' Peak_flux" \
	icmd2="colmeta -unit 'beam-1 Jy' E_Peak_flux" \
	matcher=SkyEllipse \
	params=60 \
	values1='ra_corr dec_corr a b pa' \
	values2='RA DEC Maj Min PA' \
	suffix1="" \
	suffix2="_tgss" \
	find=best1 \
	join=all1 \
	fixcols='all' \
	ocmd="addcol SepArcM_tgss 60*skyDistanceDegrees(RA_tgss,DEC_tgss,ra_corr,dec_corr)" \
	ocmd="addcol sigma_ips_tgss (hypot(Peak_flux_tgss,noise/pbcor)-noise/pbcor)/(local_rms/pbcor)" \
	ocmd="colmeta -desc 'S/N tgss would have scintillating at 100% in variability image' sigma_ips_tgss" \
	ocmd="colmeta -name Separation_tgss Separation" \
	out=${1%.vot}_allips.vot \

stilts tmatch2 \
	in1=${1%.vot}_allips.vot \
	in2=${1%.vot}_all.vot \
	icmd2='keepcols "uuid GroupID GroupSize"' \
	matcher=Exact\
	values1='uuid' \
	values2='uuid' \
	suffix1="" \
	suffix2="_1" \
	find=best1 \
	join=all1 \
	ocmd="delcols uuid_1" \
