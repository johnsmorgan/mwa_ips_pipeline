#!/usr/bin/env python
import sqlite3 as lite

def get_obsids(dbfile):
    con = lite.connect(dbfile)
    with con:
        cur = con.cursor()
        cur.execute(f"SELECT obsid FROM Observations")
        values = cur.fetchall()
    print("case $i in")
    obsids = [v[0] for v in values]
    for o, obsid in enumerate(sorted(obsids)):
        print(f"\t{o}) obsid={obsid};;")
    print("esac")

if __name__ == "__main__":
    from optparse import OptionParser, OptionValueError

    parser = OptionParser(usage = "usage: %prog dbfile")
    opts, args = parser.parse_args()

    if not len(args) == 1:
        raise OptionValueError("expecting 1 arguments")
    get_obsids(args[0])
