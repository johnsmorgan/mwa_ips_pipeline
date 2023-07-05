# mwa_ips_pipeline
Pipeline for automatic reduction of MWA IPS Data. The starting point is the following files for each observation

- `[obsid].hdf5` (an .hdf5 file containing snapshot images, continuum images and beam; only the latter is used by this pipeline)
- `[obsid]_standard.fits` (a standard continuum image)
- `[obsid]_moment2.fits` (a moment2 (variability) image).

For approximately 700 observations already processed, these data are available for team members at [pawsey data](https://data.pawsey.org.au) under the 'MWA Interplanetary Scintillation' project.

## Usage
Please contact John Morgan before using this pipeline. Co-authorship is requested if this pipeline is used for a publication, but this is negotiable.

## Pre-requisites
- bash
- python
- numpy
- astropy
- stilts
- [imstack](https://github.com/johnsmorgan/imstack)

## Catalogues needed
- GLEAM (main reference catalogue)
- VLSS (main reference catalogue outside GLEAM coverage)
- TGSSADR1 (astrometry reference catalogue)

These catalogues are also available in the expected format at [pawsey data](https://data.pawsey.org.au).

## Running the pipeline

Copy the Makefiles from the subdirectory of this pipeline into the working directory and edit as appropriate for naming conventions, and any other global variables at the top of the files that may need editing (e.g the catalogue directory, and the location of the pipeline scripts).

Assuming that the image stack is names as [obsid].hdf5, the following bash code will loop over all obsids and run Makefiles as appropriate.

```
for imstack in ??????????.hdf5
do
        obsid=${imstack%.hdf5}
        make OBSID=${obsid} -f Makefile.aegean
        #echo "Position interpolation"
        make OBSID=${obsid} -f Makefile.posinterp -j 2
        #echo "Ionospheric correction"
        make OBSID=${obsid} -f Makefile.ion -j 2
        #echo "GLEAM crossmatch"
        make OBSID=${obsid} -f Makefile.gleam -j 2
        #echo "VLSSR crossmatch"
        make OBSID=${obsid} -f Makefile.vlssr -j 2
done
```
