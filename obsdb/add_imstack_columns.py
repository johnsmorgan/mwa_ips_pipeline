import sqlite3 as lite
from optparse import OptionParser, OptionValueError

parser = OptionParser(usage = "usage: %prog filename")
opts, args = parser.parse_args()

DB_FILE = args[0]
con = lite.connect(DB_FILE)
with con:
    cur = con.cursor()
    cur.execute("ALTER TABLE Observations ADD COLUMN timeseries_nan int")
    cur.execute("ALTER TABLE Observations ADD COLUMN timeseries_zero int")
    cur.execute("ALTER TABLE Observations ADD COLUMN imstack_checksum string")
