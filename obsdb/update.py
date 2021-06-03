import os
import sqlite3 as lite
from dateutil.parser import parse

DB_FILE = "obsdb_dr1.sqlite"
con = lite.connect(DB_FILE)
with con:
    cur = con.cursor()
    cur.execute("INSERT INTO Observations(Issued, FirstC2, LastC2, FirstC3, LastC3, LastCME) VALUES(?, ?, ?, ?, ?, ?)",
                (parse("Fri May 21 01:29:56 2021"),
                 parse("2021/05/15  00:00:07.543"), #23844663.fts   first c2 
                 parse("2021/05/20  23:36:07.544"), #23845450.fts   last  c2 
                 parse("2021/05/15  00:06:07.439"), #33684338.fts   first c3 
                 parse("2021/05/20  21:42:07.425"), #33685017.fts   last  c3 
                 7 ))






