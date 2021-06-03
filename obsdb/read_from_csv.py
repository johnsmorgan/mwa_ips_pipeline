#!/usr/bin/env python
import csv
import sqlite3 as lite
from astropy.time import Time
from optparse import OptionParser

parser = OptionParser(usage = "usage: %prog dbfile csvfile")
opts, args = parser.parse_args()

con = lite.connect(args[0])
out_cols = ('obsid', 'start_time', 'obsname', 'gridpoint', 'azimuth', 'elevation', 'gal_long', 'gal_lat', 'frac_bad', 'residual', 'obs_set')
with con:
    cur = con.cursor()
    with open(args[1]) as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            out_row = []
            for out_col in out_cols:
                if out_col in row:
                    out_row.append(row[out_col])
                elif out_col == 'start_time':
                    out_row.append(Time(row['obsid'], format='gps').utc.datetime)
                elif out_col == 'obs_set':
                    for s in ('first_nw', 'first_se', 'gal_anticen', 'ecliptic_north', 'orion'):
                        if row[s] == 'true':
                            out_row.append(s)
                            break
                    else:
                        out_row.append('')
                        raise RuntimeError(f"{row['obsid']} has no set marked 'true'!")
                else:
                    raise RuntimeError(f"Don't know what to do with {out_col}")
            cur.execute("INSERT INTO Observations(obsid, start_time, obsname, gridpoint, azimuth, elevation, gal_long, gal_lat, frac_bad, residual, obs_set) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (out_row))
            print(f"{row['obsid']} inserted")
