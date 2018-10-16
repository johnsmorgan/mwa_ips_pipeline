#OBSID=1147487096
#FREQ=057-068

PIPELINE=~/Working/mwa_ips_pipeline
CAT_PATH=~/Projects/ips/catalogs/
CONTINUUM=standard
VARIABILITY=moment2

SH=/bin/bash
PYTHON=python
AEGEAN=aegean

#Aegean Settings (only need to capture strong sources so this could be set reasonably high)
SEEDCLIP=5
FLOODCLIP=4

#############################
# xmatch variability with continuum 
############################
$(OBSID)_$(FREQ)_double.vot : $(OBSID)_$(FREQ)_$(VARIABILITY)_tgss_gleam.vot $(OBSID)_$(FREQ)_$(CONTINUUM)_corr.vot
	$(SH) $(PIPELINE)/double_detections.sh $(OBSID)_$(FREQ)_$(CONTINUUM)_corr.vot $(OBSID)_$(FREQ)_$(VARIABILITY)_tgss_gleam.vot $(OBSID)_$(FREQ)_double.vot $(OBSID)_$(FREQ)_$(VARIABILITY)_no_continuum.vot

#############################
# xmatch with GLEAM
############################
$(OBSID)_$(FREQ)_$(VARIABILITY)_tgss_gleam.vot : $(OBSID)_$(FREQ)_$(VARIABILITY)_tgss.vot
	$(SH) $(PIPELINE)/match_gleam.sh $(OBSID)_$(FREQ)_$(VARIABILITY)_tgss.vot $(OBSID)_$(FREQ)_$(VARIABILITY)_tgss_gleam.vot $(CAT_PATH)

#############################
# xmatch with TGSS
############################
$(OBSID)_$(FREQ)_$(VARIABILITY)_tgss.vot : $(OBSID)_$(FREQ)_$(VARIABILITY)_corr.vot
	$(SH) $(PIPELINE)/match_tgss.sh $(OBSID)_$(FREQ)_$(VARIABILITY)_corr.vot $(CAT_PATH)
	$(PYTHON) $(PIPELINE)/get_group_significance.py $(OBSID)_$(FREQ)_$(VARIABILITY)_corr_all.vot $(OBSID)_$(FREQ)_$(VARIABILITY)_corr_good.vot $(OBSID)_$(FREQ)_$(VARIABILITY)_tgss.vot | tee $(OBSID)_$(FREQ)_$(VARIABILITY)_tgss.txt

#############################
# add ionospheric corrections
#############################
$(OBSID)_$(FREQ)_$(VARIABILITY)_corr.vot : $(OBSID)_$(FREQ)_$(CONTINUUM)_cal.vot $(OBSID)_$(FREQ)_$(VARIABILITY).vot
	$(PYTHON) $(PIPELINE)/RBF_correct.py $(OBSID)_$(FREQ)_$(CONTINUUM)_cal.vot $(FREQ) $(OBSID)_$(FREQ)_$(VARIABILITY).vot $(OBSID)_$(FREQ)_$(VARIABILITY)_corr.vot

$(OBSID)_$(FREQ)_$(CONTINUUM)_corr.vot : $(OBSID)_$(FREQ)_$(CONTINUUM)_cal.vot $(OBSID)_$(FREQ)_$(CONTINUUM).vot
	$(PYTHON) $(PIPELINE)/RBF_correct.py $(OBSID)_$(FREQ)_$(CONTINUUM)_cal.vot $(FREQ) $(OBSID)_$(FREQ)_$(CONTINUUM).vot $(OBSID)_$(FREQ)_$(CONTINUUM)_corr.vot

# ionospheric plots
#$(OBSID)_$(FREQ)_$(CONTINUUM)_cal_map.png : $(OBSID)_$(FREQ)_$(CONTINUUM)_cal.vot $(OBSID)_$(FREQ)_$(CONTINUUM).fits
#	$(PYTHON) $(PIPELINE)/RBF_ionosphere_plots.py $(OBSID)_$(FREQ)_$(CONTINUUM)_cal.vot $(FREQ) $(OBSID)_$(FREQ)_$(CONTINUUM).fits .png 

############################################
# match with calibrator catalogue
############################################
$(OBSID)_$(FREQ)_$(CONTINUUM)_cal.vot : $(OBSID)_$(FREQ)_$(CONTINUUM).vot
	$(SH) $(PIPELINE)/match_calibration.sh $(OBSID)_$(FREQ)_$(CONTINUUM).vot $(CAT_PATH) $(FREQ)


################################
# Tidy up catalogs 
################################
$(OBSID)_$(FREQ)_$(VARIABILITY).vot : $(OBSID)_$(FREQ)_$(VARIABILITY)_comp.vot
	$(PYTHON) $(PIPELINE)/make_cat.py $(OBSID).hdf5 $(OBSID)_$(FREQ)_$(VARIABILITY)_comp.vot $(OBSID)_$(FREQ)_$(VARIABILITY).vot -o $(OBSID) -v

$(OBSID)_$(FREQ)_$(CONTINUUM).vot : $(OBSID)_$(FREQ)_$(CONTINUUM)_comp.vot
	$(PYTHON) $(PIPELINE)/make_cat.py $(OBSID).hdf5 $(OBSID)_$(FREQ)_$(CONTINUUM)_comp.vot $(OBSID)_$(FREQ)_$(CONTINUUM).vot -o $(OBSID)

################################
# Aegean
################################

$(OBSID)_$(FREQ)_$(VARIABILITY)_comp.vot : $(OBSID)_$(FREQ)_$(VARIABILITY).fits
	$(AEGEAN) --seedclip=$(SEEDCLIP) --floodclip=$(FLOODCLIP) --table $(OBSID)_$(FREQ)_$(CONTINUUM).vot $(OBSID)_$(FREQ)_$(CONTINUUM).fits

$(OBSID)_$(FREQ)_$(CONTINUUM)_comp.vot : $(OBSID)_$(FREQ)_$(CONTINUUM).fits
	$(AEGEAN) --seedclip=$(SEEDCLIP) --floodclip=$(FLOODCLIP) --table $(OBSID)_$(FREQ)_$(CONTINUUM).vot $(OBSID)_$(FREQ)_$(CONTINUUM).fits
