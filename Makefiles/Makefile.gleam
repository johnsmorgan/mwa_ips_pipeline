FREQ=121-132
PIPELINE=~/Working/mwa_ips_pipeline
CAT_PATH=/data/ips/catalogs
SH=/bin/bash
PYTHON=python
#OUTNAME=dr1
#DBFILE=../../ips_phase2_dr1.sqlite
SUFFIX=gleam
RA=RAJ2000
DE=DEJ2000

GLEAM_TARGETS : $(OBSID)_$(SUFFIX)_digest.fits $(OBSID)_no_$(SUFFIX).vot $(OBSID)_no_$(SUFFIX)_moment2.vot

$(OBSID)_${SUFFIX}_digest.fits : $(OBSID)_$(SUFFIX).vot 
	$(SH) $(PIPELINE)/make_digest.sh  $(OBSID)_$(SUFFIX).vot $(OBSID)_${SUFFIX}_digest.fits

$(OBSID)_no_${SUFFIX}.vot : $(OBSID)_infield_$(SUFFIX).vot $(OBSID)_$(FREQ)_image_corr.vot
	bash $(PIPELINE)/nomatch.sh $(OBSID)_infield_$(SUFFIX).vot $(OBSID)_$(FREQ)_image_corr.vot $(OBSID)_no_$(SUFFIX).vot

$(OBSID)_no_${SUFFIX}_moment2.vot : $(OBSID)_infield_$(SUFFIX).vot $(OBSID)_$(FREQ)_image_moment2_corr.vot
	bash $(PIPELINE)/nomatch.sh $(OBSID)_infield_$(SUFFIX).vot $(OBSID)_$(FREQ)_image_moment2_corr.vot $(OBSID)_no_$(SUFFIX)_moment2.vot

$(OBSID)_$(SUFFIX).vot : $(OBSID)_detections_$(SUFFIX).vot
	#topcat -stilts tpipe omode=meta in=$(OBSID)_detections_$(SUFFIX).vot
	$(PYTHON) $(PIPELINE)/add_nsi2.py $(OBSID)_detections_$(SUFFIX).vot $(OBSID)_$(SUFFIX).vot --ra_col=$(RA) --dec_col=$(DE)

$(OBSID)_detections_$(SUFFIX).vot : $(OBSID)_infield_$(SUFFIX).vot $(OBSID)_$(FREQ)_image_corr.vot $(OBSID)_$(FREQ)_image_moment2_corr.vot
	$(SH) $(PIPELINE)/match_master.sh  $(OBSID)_infield_$(SUFFIX).vot $(OBSID)_$(FREQ)_image_corr.vot $(OBSID)_$(FREQ)_image_moment2_corr.vot $(OBSID)_detections_$(SUFFIX).vot $(RA) $(DE)

$(OBSID)_infield_$(SUFFIX).vot : $(OBSID)_beam.hdf5 
	$(PYTHON) $(PIPELINE)/make_obs_cat.py $(OBSID)_beam.hdf5 $(CAT_PATH)/gleam_ips_bands.fits $(OBSID)_infield_$(SUFFIX).vot --ra_col=$(RA) --dec_col=$(DE)
