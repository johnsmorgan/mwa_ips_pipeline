topcat -stilts tpipe \
	in=$1 \
	cmd='keepcols "GLEAM RAJ2000 DEJ2000 Fp162 elongation2 sun_lat limb mpt1 mpt2 pbcor pbcor_norm ra_corr dec_corr peak_flux local_rms snr ra_corr_2  dec_corr_2 dS snr_2 Separation_2 dS2 local_rms2 snr_scint"' \
	cmd='replacecol RAJ2000 toFloat(RAJ2000)' \
	cmd='replacecol DEJ2000 toFloat(DEJ2000)' \
	cmd='replacecol Fp162 toFloat(Fp162)' \
	cmd='replacecol elongation2 toFloat(elongation2)' \
	cmd='replacecol sun_lat toFloat(sun_lat)' \
	cmd='replacecol mpt1 toFloat(mpt1)' \
	cmd='replacecol mpt2 toFloat(mpt2)' \
	cmd='replacecol pbcor toFloat(pbcor)' \
	cmd='replacecol pbcor_norm toFloat(pbcor_norm)' \
	cmd='replacecol ra_corr toFloat(ra_corr)' \
	cmd='replacecol dec_corr toFloat(dec_corr)' \
	cmd='replacecol peak_flux toFloat(peak_flux)' \
	cmd='replacecol local_rms toFloat(local_rms)' \
	cmd='replacecol snr toFloat(snr)' \
	cmd='replacecol dS toFloat(dS)' \
	cmd='replacecol ra_corr_2 toFloat(ra_corr_2)' \
	cmd='replacecol dec_corr_2 toFloat(dec_corr_2)' \
	cmd='replacecol dS2 toFloat(dS2)' \
	cmd='replacecol local_rms2 toFloat(local_rms2)' \
	cmd='replacecol Separation_2 toFloat(Separation_2)' \
	cmd='replacecol snr_scint toFloat(snr_scint)' \
	out=$2


#     1: GLEAM(String)
#     2: RAJ2000(Double)/deg
#     3: DEJ2000(Double)/deg
#     4: Fp162(Double)
#     5: elongation2(Double)
#     6: sun_lat(Double)
#     7: limb(Character)
#     8: mpt1(Double)
#     9: mpt2(Double)
#    10: pbcor(Double)
#    11: pbcor_norm(Double)
#    12: ra_corr(Double)/deg
#    13: dec_corr(Double)/deg
#    14: peak_flux(Double)
#    15: local_rms(Float)
#    16: snr(Double)
#    17: ra_corr_2(Double)/deg
#    18: dec_corr_2(Double)/deg
#    19: dS(Double)
#    20: snr_2(Double)
#    21: Separation_2(Double) - Normalised distance between ellipses; range is 0 (concentric) - 2
#     (tangent)
#    22: dS2(Double)
#    23: local_rms2(Double)
#    24: snr_scint(Double)