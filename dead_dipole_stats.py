#!/usr/bin/env python
from collections import Counter
import os, sys
from optparse import OptionParser
import numpy as np
from astropy.io import fits
from astropy.time import Time
import matplotlib.pyplot as plt

N_POL = 2

parser = OptionParser(usage="usage: %prog metafits_path\nFirst 10 characters of metafits file is taken to be obsid")
parser.add_option("--out_suffix", dest="suffix", default="_plot.png", help="output suffix, can include any supported matplotlib format (default %default")
parser.add_option("--no_plot", action='store_true', dest="no_plot", help="no plot")
parser.add_option("--csv", action='store_true', dest="csv", help="write out csv line")
parser.add_option("--csv_header", action='store_true', dest="csv_header", help="write out csv head line and quit")

opts, args = parser.parse_args()
if opts.csv_header:
    print "obsid,utc,n_tile_flag,n_tile_dipole_flag,n_tile_flag_total,x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11,x12,x13,x14,x15,x16,y1,y2,y3,y4,y5,y6,y7,y8,y9,y10,y11,y12,y13,y14,y15,y16"
    sys.exit()

if len(args) != 1:
    parser.error("incorrect number of arguments")

obsid = int(os.path.split(args[0])[1][:10])
timestring = Time(obsid, format='gps').utc.isot
hdus = fits.open(args[0])
n_tile = len(hdus[1].data)/float(N_POL)
pol = hdus[1].data['Pol']
tile_flags = hdus[1].data['Flag']
dipole_flags = hdus[1].data['Delays'] == 32

# identify tiles that will (by default) be flagged by cotter
# due to dipole flags
dipole_tile_flags = np.zeros(tile_flags.shape, dtype=np.bool)

for a in sorted(set(hdus[1].data['Antenna'])):
    ant_idx = hdus[1].data['Antenna'] == a
    if np.max(np.sum(dipole_flags[ant_idx], axis=1)) > 1:
        dipole_tile_flags[ant_idx] = True

all_tile_flags = dipole_tile_flags | tile_flags
if not opts.csv:
    print obsid,
    print timestring
    print "%d/%d tiles flagged due to tile flags" % (np.sum(tile_flags)/N_POL, n_tile)
    print "%d/%d tiles flagged due to bad dipoles according to cotter default criteria" % (np.sum(dipole_tile_flags)/N_POL, n_tile)
    print "%d/%d tiles flagged in total" % (np.sum(all_tile_flags)/N_POL, n_tile)
else:
    out_line = ""
    out_line += "%d,%s,%d,%d,%d," % (obsid, timestring, np.sum(tile_flags)/N_POL, np.sum(dipole_tile_flags)/N_POL, np.sum(all_tile_flags)/N_POL)

#fig = plt.figure()
#gs = fig.add_gridspec(1, 2)
#ax1 = fig.add_subplot(gs[0, 0])
#ax2 = fig.add_subplot(gs[0, 1])

#print dipole_flags.shape
#print dipole_flags[(~all_tile_flags) & (pol == 'X')].shape
x_filter = (~all_tile_flags) & (pol == 'X')
y_filter = (~all_tile_flags) & (pol == 'Y')
#print x_filter.shape
#print dipole_flags[np.where(x_filter)].shape
#print dipole_flags[np.where(y_filter)].shape
x_sum = np.sum(dipole_flags[np.where(x_filter)], axis=0)
y_sum = np.sum(dipole_flags[np.where(y_filter)], axis=0)

x_sum1 = np.sum(dipole_flags[np.where(x_filter)], axis=1) # by tile breakdown
y_sum1 = np.sum(dipole_flags[np.where(y_filter)], axis=1) # by tile breakdown

if not opts.csv:
    print "sum dipole flags by dipole x: %s" % (x_sum)
    print "sum dipole flags by dipole y: %s" % (y_sum)
else:
    out_line += ','.join((str(s) for s in x_sum))
    out_line += ','
    out_line += ','.join((str(s) for s in y_sum))
    print out_line

if not opts.no_plot:
    max_ = np.max(np.stack((x_sum, y_sum)))
    fig = plt.figure()
    fig.suptitle("%d %s\n%d tiles, %d flagged tiles , %d dipole flagged tiles, %d total flagged tiles\n colour scale max=%d\nX: %s Y:%s X|Y:%s" % (obsid, timestring,
                                                                                                                                                   n_tile, np.sum(tile_flags)/N_POL, np.sum(dipole_tile_flags)/N_POL, np.sum(all_tile_flags)/N_POL,
                                                                                                                                                   max_,
                                                                                                                                                   str(Counter(x_sum1))[8:-1], str(Counter(y_sum1))[8:-1], str(Counter(y_sum1+x_sum1))[8:-1]))


    plt.subplot(1, 2, 1)
    plt.title("X")
    plt.imshow(x_sum.reshape(4, 4))
    plt.clim(0, max_)
    plt.xticks([])
    plt.yticks([])
    plt.subplot(1, 2, 2)
    plt.title("Y")
    plt.imshow(y_sum.reshape(4, 4))
    plt.clim(0, max_)
    plt.xticks([])
    plt.yticks([])
    plt.savefig("%d%s" % (obsid, opts.suffix))
