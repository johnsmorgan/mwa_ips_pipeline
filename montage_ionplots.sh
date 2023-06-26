obsid=$1
#-geometry 16x16+1+1
# see https://legacy.imagemagick.org/Usage/montage/#zero_geometry
montage ${obsid}_121-132_ion_xy_raw.png ${obsid}_121-132_ion_xy_corr.png -geometry '1x1+0+0<' -tile 1x2 ${obsid}_121-132_ion_xy.png
montage ${obsid}_121-132_ion_map.png ${obsid}_121-132_ion_xy.png  -tile 2x1  -geometry '1x1+0+0<'  ${obsid}_121-132_ionplot.png
