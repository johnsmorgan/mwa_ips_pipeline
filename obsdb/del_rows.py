#!/usr/bin/env python
import csv
import sqlite3 as lite
from astropy.time import Time
from optparse import OptionParser

OBSID_COL="obsid"
parser = OptionParser(usage = "usage: %prog dbfile csvfile")
parser.add_option("--obsid_col", dest="obsid_col", default=OBSID_COL, help="obsid column in input csv file")
parser.add_option("-n", "--dry_run", dest="dry_run", action="store_true", help="dry run (lists obsid instead")
opts, args = parser.parse_args()

con = lite.connect(args[0])
with con:
    cur = con.cursor()
    with open(args[1]) as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            obsid=int(row[opts.obsid_col])
            if opts.dry_run:
                cur.execute("SELECT * FROM Observations WHERE obsid==?", (obsid,))
                values = cur.fetchone()
                print(values)
            else:
                cur.execute("DELETE FROM Observations WHERE obsid==?", (obsid,))
                print(f"{obsid} deleted")
