#!/bin/bash
set -eou pipefail
suffix=all
topcat -stilts tcat \
	in=@$1 \
	icmd='keepcols "background local_rms ra err_ra dec err_dec a b pa uuid elongation snr pbcor pbcor_norm dS err_dS ra_corr dec_corr Source_name_tgss RA_tgss DEC_tgss Maj_tgss Min_tgss PA_tgss Peak_flux_tgss E_Peak_flux_tgss Source_code_tgss Separation_tgss SepArcM_tgss sigma_ips_tgss GroupID GroupSize" ' \
	loccol='obsid' \
	ocmd="replacecol obsid substring(obsid,$3,$4)" \
	out=$2

	#icmd='select pbcor_norm>0.25' \
	#icmd='keepcols "ra dec ra_corr dec_corr elongation snr"' \
	#ocmd='keepcols "source_name_tgss p_match1 obsid RA_tgss DEC_tgss elongation pbcor_norm sigma_ips_tgss"' \
