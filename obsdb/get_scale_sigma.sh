#!/bin/bash
#set -x
set -euo pipefail
obsid=$1
csv=$2
sqlitedb=$3
script_dir=$(dirname "$0")
for i in {2..5}
do
	val=$(echo $csv | cut -d ',' -f $i)
	case $i in
		2) param=sigma_x;;
		3) param=sigma_y;;
		4) param=scale_x;;
		5) param=scale_y;;
	esac
	${script_dir}/set_parameter.py $sqlitedb ${obsid} $param $val --overwrite
done

