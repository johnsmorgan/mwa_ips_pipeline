# match against position and flux density calibration catalogue
case $3 in
	057-068)centroid=080;;
	121-132)centroid=162;;
esac

stilts tmatch2 \
        in1=$1 \
        in2=$2/ips_continuum_cal.fits \
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

stilts tmatch2 \
        in1=$1 \
        in2=$2/ips_continuum_cal.fits \
	icmd2='colmeta -name ra $1' \
	icmd2='colmeta -name dec $2' \
        matcher=skyEllipse \
        values1="ra dec a b pa" \
        values2="ra dec 0 0 0" \
        suffix1="" \
        suffix2="_cat" \
	find="best2" \
	join="all1" \
        params=60 \
        out=${1%.vot}_cal.vot

stilts tmatch2 \
        in1=${1%.vot}_cal.vot \
        in2=${1%.vot}_cal_all.vot \
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
        out=${1%.vot}_cal.vot
rm ${1%.vot}_cal_all.vot

stilts tpipe \
        in=${1%.vot}_cal.vot \
	cmd="select '!complex'" \
	cmd="addcol flux_ratio Fp${centroid}/peak_flux" \
	cmd="keepcols 'flux_ratio'" \
	cmd='rowrange 1 +50' \
	cmd="stats Quartile2" \
        out=${1%.vot}_flux_ratio.csv
	ofmt=csv
