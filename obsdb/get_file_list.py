#!/usr/bin/env python
import os
import sqlite3 as lite

def get_filelist(dbfile, root, suffix):
    con = lite.connect(dbfile)
    with con:
        cur = con.cursor()
        cur.execute(f"SELECT obsid FROM Observations")
        values = cur.fetchall()
    obsids = [v[0] for v in values]
    for obsid in sorted(obsids):
        print(os.path.join(root, str(obsid), str(obsid)+suffix))

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('dbfile', help='sqlite database')
    parser.add_argument('root', help='root directory')
    parser.add_argument('suffix', help='root directory')
    args = parser.parse_args()
    get_filelist(args.dbfile, args.root, args.suffix)
