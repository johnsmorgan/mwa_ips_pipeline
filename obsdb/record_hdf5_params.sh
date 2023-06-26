#!/bin/bash
set -euo pipefail
#set -x
obsid=$1
csv=$2
sqlitedb=$3
script_dir=$(dirname "$0")
for i in {1..4}
do
	val=$(echo $csv | cut -d ',' -f $i)
	case $i in
		1) param=imstack_size;;
		2) param=timeseries_nan;;
		3) param=timeseries_zero;;
		4) param=imstack_checksum;;
	esac
	${script_dir}/set_parameter.py $sqlitedb ${obsid} $param $val --overwrite
done
