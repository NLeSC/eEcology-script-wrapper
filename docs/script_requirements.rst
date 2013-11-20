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
* **Arguments** that are required to run script. Includes order, format, possible choices, db credentials and db connection string. An input form will be made based on the arguments.

Database
========

The script will be executed with the database privileges of the end-user.
This means only use table/views everyone can use eg. only use ``\*_limited`` views.

The database stores datetime with UTC timezone. Datetimes from the submit form are also in UTC timezone.
Inside script make sure you use **UTC timezone** when quering database and generating output.

Matlab
======

* The script should start with a function which takes only **strings as arguments**. The reason is that the script will be compiled and started from command-line. The arguments can be converted to Matlab native variables using ``val = eval(valAsStr)``.
* Use the **OpenEarth PostgreSQL library** to perform database queries. For more information see https://services.e-ecology.sara.nl/redmine/projects/uvagps/wiki/Matlab_with_OpenEarth
* Standard out and error are saved as ``stdout.txt`` and ``stderr.txt`` resp.
* Script will be run inside the result directory so any generated output file should have no directory prefixed to it.
* Do not use hardcoded absolute paths in script, as the machine where it is compiled or being run may not have those paths.
* The script must be compiled for Linux so it can be run without a Matlab installation, to compile some information is required:

  * The version of Matlab
  * Required toolboxes
  * Additional Matlab files needed to run script.

Example Matlab script to find number of timepoints of a tracker in a certain date range:

.. code-block:: matlab

    function db_query(dbUsername, dbPassword, dbName, databaseHost,...
                      TrackerIdentifier, startTime, stopTime)
    conn = pg_connectdb(dbName, 'host', databaseHost,...
                        'user', dbUsername, 'pass', dbPassword);
    sql_tpl = ['SELECT device_info_serial, count(*) ',...
           'FROM gps.uva_tracking_limited ',...
           'WHERE device_info_serial=%d ',...
           'AND date_time BETWEEN ''%s'' AND %s'' ',...
           'GROUP BY device_info_serial'];
    sql = sprintf(sql_tpl, TrackerIdentifier, starTime, stopTime)
    results = pg_fetch_struct(conn, sql);
    display(results);

R
=

* Python list variables have to converted to R vectors using eg. ``rpy2.robjects.IntVector([1,2,3])`` (For more information see http://rpy.sourceforge.net/rpy2/doc-2.2/html/introduction.html#r-vectors)
* To write output files to the ``output_dir``, it has to be passed a R function argument

Example R script to find number of timepoints of a tracker in a certain date range:

.. code-block:: r

    db_query <- function(dbUsername, dbPassword, dbName, databaseHost,
                         TrackerIdentifier, startTime, stopTime, outputDir) {
        library(RPostgreSQL)
        library(stringr)
        drv <- dbDriver("PostgreSQL")
        conn = dbConnect(drv, user=dbUsername, password=dbPassword,
                         dbname=dbName, host=databaseHost)

        tpl <- paste("SELECT device_info_serial, count(*) FROM gps.uva_tracking_limited ",
           "WHERE device_info_serial="%s ",
           "AND date_time BETWEEN '%s' AND '%s' ",
           "GROUP BY device_info_serial")
        sql =  sprintf(tpl, TrackerIdentifier, startTime, stopTime)

        results <- dbGetQuery(conn, sql)

        dbDisconnect(conn)

        # Save as text
        dump('results', file=file.path(outputDir, "results.txt"))
    }

Python
======

Use SQLAlchemy models of e-ecology database.

Example Python run function to find number of timepoints of a tracker in a certain date range:

.. code-block:: python

    def run(self, db_url, tracker_id, start, end):
        # Perform a database query
        s = DBSession(db_url)()
        q = s.query(Tracking)
        q = q.filter(Tracking.device_info_serial==tracker_id)
        q = q.filter(Tracking.date_time.between(start, end))
        count = q.count()

        s.close()

        # Write results to text files
        fn = os.path.join(self.output_dir(), 'result.txt')
        with open(fn, 'w') as f:
            f.write(count)
        return {'query': {'start': start,
                          'end': end,
                          'tracker_id': tracker_id,
                          }}


