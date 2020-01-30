#!/usr/bin/env bash
set -euo pipefail
# add ecliptic latitude and longitude, and ecliptic longitude relative to sun to input file
# inputs:
# 
# infile (required)
# sun longitude in degrees (required)
# outfile (optional; default:infile)
# ra_col (optional; default:ra_tgss)
# dec_col (optional; default:dec_tgss)
# lon_col (optional; default:lon)
# lat_col (optional; default:lat)
# sun_lon_col (optional; default:sun_lon)
infile=$1
sun_lon=$2
outfile=${3:-$1}
ra_col=${4:-ra_tgss}
dec_col=${5:-dec_tgss}
lon_col=${6:-lon}
lat_col=${7:-lat}
sun_lon_col=${8:-sun_lon}

stilts tpipe \
	in=${1} \
	cmd="addskycoords fk5 ecliptic $ra_col $dec_col $lon_col $lat_col" \
	cmd="addcol $sun_lon_col (($lon_col-$2)%360)" \
	cmd="replacecol $sun_lon_col $sun_lon_col<0?$sun_lon_col+360:$sun_lon_col" \
	out=$outfile
