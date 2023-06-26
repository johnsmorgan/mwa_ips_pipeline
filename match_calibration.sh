#!/usr/bin/env bash
set -euo pipefail
# match against position and flux density calibration catalogue
case $3 in
	057-068)centroid=080;;
	121-132)centroid=162;;
esac

echo
echo find all matches for input file and record all rows for input file
topcat -stilts tmatch2 \
        in1=$1 \
        in2=$2 \
	icmd2='colmeta -name ra $1' \
	icmd2='colmeta -name dec $2' \
        matcher=skyEllipse \
        values1="ra dec a b pa" \
        values2="ra dec 0 0 0" \
        suffix1="" \
        suffix2="_cat" \
	find="all" \
	join="all1" \
        params=60 \
        out=${1%.vot}_cal_all.vot

echo
echo find all matches for input file and record only rows with matches
topcat -stilts tmatch2 \
        in1=$1 \
        in2=$2 \
	icmd2='colmeta -name ra $1' \
	icmd2='colmeta -name dec $2' \
        matcher=skyEllipse \
        values1="ra dec a b pa" \
        values2="ra dec 0 0 0" \
        suffix1="" \
        suffix2="_cat" \
	find="best2" \
	join="1and2" \
        params=60 \
        out=${1%.vot}_cal.vot

echo
echo mark all rows with more than one match as complex in final catalogue
echo or just add empty columns
topcat -stilts tmatch2 \
	in1=${1%.vot}_cal.vot \
	in2=${1%.vot}_cal_all.vot \
	icmd1='colmeta -name Separation_cat Separation' \
	icmd2='keepcols "uuid GroupID GroupSize"' \
	matcher=Exact\
	values1='uuid' \
	values2='uuid' \
	suffix1="" \
	suffix2="_1" \
	fixcols=all \
	find=best1 \
	join=all1 \
	ocmd="addcol complex !NULL_GroupID_1||!NULL_GroupID_1" \
	ocmd='delcols "uuid_1 GroupID GroupSize GroupID_1 GroupSize_1"' \
	ocmd='keepcols "ra err_ra dec err_dec peak_flux local_rms snr pbcor pbcor_norm ra_cat dec_cat Fp080 Fp162 Separation_cat complex GroupID GroupSize uuid"' \
	out=${4} || topcat -stilts tpipe \
        in=${1%.vot}_cal.vot \
	cmd='colmeta -name Separation_cat Separation' \
	cmd="addcol complex false" \
	cmd="addcol GroupID NULL" \
	cmd="addcol GroupSize NULL" \
	cmd='keepcols "ra err_ra dec err_dec peak_flux local_rms snr pbcor pbcor_norm ra_cat dec_cat Fp080 Fp162 Separation_cat complex GroupID GroupSize uuid"' \
	out=$4

echo
echo #remove intermediate files
if [ ! $4 == ${1%.vot}_cal.vot ]; then
	rm ${1%.vot}_cal.vot
fi

if [ ! $4 == ${1%.vot}_cal_all.vot ]; then
	rm ${1%.vot}_cal_all.vot
fi

echo
echo #record flux ratio
topcat -stilts tpipe \
        in=$4 \
	cmd="select '!complex'" \
	cmd='select "pbcor_norm>0.5"' \
	cmd="sorthead -down 50 peak_flux/local_rms" \
	cmd="addcol flux_ratio Fp${centroid}*pbcor/peak_flux" \
	cmd="keepcols 'flux_ratio'" \
	cmd='rowrange 1 +50' \
	cmd="stats Quartile2" \
        out=${1%.vot}_flux_ratio.csv \
	ofmt=csv
