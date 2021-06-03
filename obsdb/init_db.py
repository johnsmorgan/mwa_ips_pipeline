import sqlite3 as lite
from optparse import OptionParser, OptionValueError

parser = OptionParser(usage = "usage: %prog filename")
opts, args = parser.parse_args()

DB_FILE = args[0]
con = lite.connect(DB_FILE)
with con:
    cur = con.cursor()
    cur.execute("CREATE TABLE Observations(obsid int primary key, start_time date, obsname string, gridpoint int, azimuth float, elevation float, gal_long float, gal_lat float, frac_bad float, residual float, obs_set string, imstack_size int, scale_x float, scale_y float, sigma_x float, sigma_y float, continuum_nan int, moment2_nan int, continuum_detections int, moment2_detections int, ionomag float, iono_pca float, moment2_tgss_matches int)")
