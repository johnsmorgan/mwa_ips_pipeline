# mwa_ips_pipeline
Pipeline for automatic reduction of MWA IPS Data

## Pre-requisites
bash
python
- numpy
- astropy
stilts

## Catalogues needed
GLEAM
TGSS ADR 1
Callingham
MRC
VLSS

## Run before first use of pipeline

gleam_ips_bands - to produce a new GLEAM catalogue containing only the MWA IPS bands and flags for which category (if any) the source is in Callingham et al.

ips_continuum_cal - produce a catalog of all VLSS sources in area covered by VLSS (MRC elsewhere), removing any sources within 3 arcminutes of each other --used for absolute flux calibration (not yet      implemented) and correction of ionospheric refraction.

## Running the pipeline

Put image_stack (.hdf5 file), variability image and standard image in directory with the following naming conventions
[OBSID].hdf5
[OBSID]_standard.fits
[OBSID]_moment2.fits

Copy makefile into the same directory and edit as appropriate

run `make`
