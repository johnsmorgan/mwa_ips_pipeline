#!/bin/bash
set -eou pipefail
suffix=all
topcat -stilts tcat \
	in=@$1 \
	icmd='keepcols "RA_tgss DEC_tgss ra dec ra_corr dec_corr source_name_tgss p_match1 name_match2 p_match2 GLEAM Fp162 elongation pbcor_norm snr sigma_ips_tgss Sep*"' \
	loccol='obsid' \
	ocmd="replacecol obsid substring(obsid,$3,$4)" \
	out=$2
	#ocmd='keepcols "source_name_tgss p_match1 obsid RA_tgss DEC_tgss elongation pbcor_norm sigma_ips_tgss"' \
