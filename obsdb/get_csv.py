#!/usr/bin/env python
import sqlite3 as lite

PARAMETERS = {'imstack_size': int,
              'scale_x': float,
              'scale_y': float,
              'sigma_x': float,
              'sigma_y': float,
              'timeseries_nan': int,
              'timeseries_zero': int,
              'imstack_checksum': str,
              'continuum_nan': int,
              'moment2_nan': int,
              'continuum_detections': int,
              'moment2_detections': int,
              'ionomag': float,
              'iono_pca': float,
              'moment2_tgss_matches': int}

def get_all(dbfile):
    con = lite.connect(dbfile)
    with con:
        cur = con.cursor()
        cur.execute(f"SELECT obsid, imstack_size, scale_x, scale_y, sigma_x, sigma_y, timeseries_nan, timeseries_zero, imstack_checksum, continuum_nan, moment2_nan, continuum_detections, moment2_detections, moment2_tgss_matches FROM Observations")
        print("obsid,imstack_size,scale_x,scale_y,sigma_x,sigma_y,timeseries_nan,timeseries_zero,imstack_checksum,continuum_nan,moment2_nan,continuum_detections,moment2_detections,moment2_tgss_matches")
        values = cur.fetchall()
        for line in values:
            print(','.join((str(l) if l is not None else "" for l in line)))

if __name__ == "__main__":
    from optparse import OptionParser, OptionValueError

    parser = OptionParser(usage = "usage: %prog dbfile")
    opts, args = parser.parse_args()

    if not len(args) == 1:
        raise OptionValueError("expecting 1 arguments")
    get_all(args[0])
