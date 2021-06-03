import sqlite3 as lite

PARAMETERS = {'imstack_size': int,
              'scale_x': float,
              'scale_y': float,
              'sigma_x': float,
              'sigma_y': float,
              'continuum_nan': int,
              'moment2_nan': int,
              'continuum_detections': int,
              'moment2_detections': int,
              'ionomag': float,
              'iono_pca': float,
              'moment2_tgss_matches': int}

def set_parameter(dbfile, obsid, parameter, value):
    con = lite.connect(dbfile)
    obsid = int(obsid)
    value = PARAMETERS[parameter](value)
    if not parameter in PARAMETERS:
        raise TypeError(f"{parameter} not recognised")
    with con:
        cur = con.cursor()
        cur.execute(f"SELECT {parameter} FROM Observations WHERE obsid=?", (obsid,))
        value1 = cur.fetchone()
        if value1 is None:
            raise RuntimeError(f"obsid {obsid} not in database")
        if value1[0] is not None:
            if opts.overwrite:
                print(f"Overwriting existing parameter : {value1[0]}")
            else:
                raise RuntimeError("parameter is already set")
        cur.execute(f"UPDATE Observations SET {parameter}=? WHERE obsid=?", (value, obsid))

if __name__ == "__main__":
    from optparse import OptionParser, OptionValueError

    parser = OptionParser(usage = "usage: %prog dbfile obsid parameter value")
    parser.add_option("--overwrite", dest="overwrite", action="store_true", help="allow overwrite if parameter is already set")
    opts, args = parser.parse_args()

    if not len(args) == 4:
        raise OptionValueError("expecting 4 arguments")
    dbfile = args[0]
    obsid = args[1]
    parameter = args[2]
    if not parameter in PARAMETERS:
        raise OptionValueError(f"{parameter} not recognised")
    value = args[3]

    set_parameter(dbfile, obsid, parameter, value)
