#!/bin/bash
stilts tpipe \
	in=$1 \
	out=$2 \
	cmd="addcol snr peak_flux/local_rms" \
	cmd='sort -down snr' \
	cmd='keepcols "ra dec a b pa peak_flux local_rms snr uuid"'
