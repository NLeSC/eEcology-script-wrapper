===================
Script requirements
===================

Requirements where the script that is added needs to adhere to.

.. contents:: Requirements
    :local:

General
=======

Several pieces of information about the script are required:

* **Id**, identifier of the script, will be used in package and url.
* **Name**, Human readable name.
* **Description**, short description of script.
* **Arguments** that are required to run script. Includes order, format, possible choices, db credentials and db connection string.

Database
========

The script will be executed with the database privileges of the end-user. This means only use table/views everyone can use eg. only use ``\*_limited`` views.

Matlab
======

* The script should start with a function which takes only **strings as arguments**. The reason is that the script will be compiled and started from command-line. The arguments can be converted to Matlab native variables using ``val = eval(valAsStr)``.
* Use the **OpenEarth PostgreSQL library** to perform database queries. For more information see https://publicwiki.deltares.nl/display/OET/PostgreSQL+access+with+Matlab
* Standard out and error are saved as ``stdout.txt`` and ``stderr.txt`` resp.
* Script will be run inside a directory so any generated output file should have no directory prefixed to it.

Example Matlab script to find number of timepoints of a tracker in a certain date range:

.. code-block:: matlab

    function db_query(dbUsername, dbPassword, dbName, databaseHost, TrackerIdentifier, startTime, stopTime)
    conn = pg_connectdb(dbName, 'host', databaseHost, 'user', dbUsername, 'pass', dbPassword, 'database_toolbox', 0);
    sql = ['SELECT device_info_serial, count(*) ',...
           'FROM gps.uva_tracking_limited ',...
           'WHERE device_info_serial=',TrackerIdentifier,' ',...
           'AND date_time BETWEEN ',char(39) , startTime,char(39) ,...
           ' AND ',char(39) , stopTime, char(39), ' ',...
           'GROUP BY device_info_serial'];
    results = pg_fetch(conn, sql);
    display(results);

R
=

* Python list variables have to converted to R vectors using eg. ``robjects.IntVector([1,2,3])`` (For more information see http://rpy.sourceforge.net/rpy2/doc-2.2/html/introduction.html#r-vectors)
* To write output files to the ``output_dir``, it has to be passed a R function argument

Example R script to find number of timepoints of a tracker in a certain date range:

.. code-block:: r

    db_query <- function(dbUsername, dbPassword, dbName, databaseHost, TrackerIdentifier, startTime, stopTime, outputDir) {
        library(RPostgreSQL)
        library(stringr)
        drv <- dbDriver("PostgreSQL")
        conn = dbConnect(drv, user=dbUsername, password=dbPassword, dbname=dbName, host=databaseHost)

        sql <- paste("SELECT device_info_serial, count(*) FROM gps.uva_tracking_limited ",
           "WHERE device_info_serial=",TrackerIdentifier, " ",
           "AND date_time BETWEEN '", startTime,"' AND '",stopTime, "'",
           "GROUP BY device_info_serial")

        results <- dbGetQuery(conn, sql)

        # Save as text
        dump('results', file=file.path(outputDir, "results.txt"))
    }

Python
======

* Use SQLAlchemy models of e-ecology database

Example Python run function to find number of timepoints of a tracker in a certain date range:

.. code-block:: python

    def run(self, db_url, tracker, start, end):
        # Perform a database query
        q = DBSession(db_url).query(Tracking)
        q = q.filter(Tracking.device_info_serial==tracker)
        q = q.filter(Tracking.date_time.between(start, end))
        count = q.count()

        s.close_all()

        # Write results to text files
        fn = os.path.join(self.output_dir, 'result.txt')
        with open(fn, 'w') as f:
            f.write(count)
        return {'files': {'result.txt': fn}}


