# mwa_ips_pipeline
Pipeline for automatic reduction of MWA IPS Data

## Pre-requisites
- bash
- python
- numpy
- astropy
- stilts

## Catalogues needed
- GLEAM
- Callingham
- VLSS

## Running the pipeline

Put image_stack (.hdf5 file), variability image and standard image in directory with the following naming conventions
- [OBSID].hdf5
- [OBSID]_standard.fits
- [OBSID]_moment2.fits

Note that the standard names for the latter two can be edited in the makefile.

Copy makefile into the same directory and edit as appropriate

run `make`
