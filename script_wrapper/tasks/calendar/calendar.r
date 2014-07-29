calendar <- function(dbUsername, dbPassword, dbName, databaseHost, TrackerIdentifier, startTime, stopTime, outputDir) {
    # Run in R with:
    # source('dbq.r')
    # calendar('****', '****, 'eecology', 'eecology db.e-ecology.sara.nl', 620, '2010-07-01T00:00:00', '2010-09-01T00:00:00', '/tmp')
    library(RPostgreSQL)
    drv <- dbDriver("PostgreSQL")
    conn = dbConnect(drv, user=dbUsername, password=dbPassword, dbname=dbName, host=databaseHost)

    spheroid = 'SPHEROID["WGS 84",6378137,298.257223563]'

    tpl <- paste(
        "SELECT ",
        "* ",
        "FROM (",
        "  SELECT ",
        "    date(date_time) as date, ",
        "    count(*) as fixes, ",
        # Lengt of line of point == distance, see http://gis.stackexchange.com/questions/19369/total-great-circle-distance-along-a-path-of-points-postgis
        "    round((ST_Length_Spheroid(ST_MakeLine(location),'%s')/1000.0)::numeric, 3) AS distance, ",
        "    max(altitude) as maxalt, round(avg(altitude)::numeric, 2) as avgalt, min(altitude) as minalt, ",
        "    max(tr.temperature) as maxtemp, round(avg(tr.temperature)::numeric, 2) as avgtemp, min(tr.temperature) as mintemp ",
        # Make sure locations are ordered by date_time, see http://postgis.refractions.net/documentation/manual-1.5/ST_MakeLine.html
        "  FROM (SELECT * FROM gps.ee_tracking_speed_limited ",
        "  WHERE device_info_serial=%s AND date_time BETWEEN '%s' AND '%s' ",
        "  AND longitude IS NOT NULL AND userflag<>1 ORDER BY date_time ) tr",
        "  GROUP BY date(date_time) ",
        ") t ",
        # Add energy
        "FULL JOIN ( ",
        "  SELECT date(date_time) as date, min(vbat) as minvbat ",
        "  FROM gps.ee_energy_limited ",
        "  WHERE device_info_serial=%s AND date_time BETWEEN '%s' AND '%s' ",
        "  GROUP BY date(date_time) ",
        ") e USING (date) ",
        # Add accelerometer
        "LEFT JOIN ( ",
        "  SELECT date(date_time) as date, count(*) as accels ",
        "  FROM gps.ee_tracking_speed_limited ",
        "  JOIN gps.ee_acceleration_limited USING (device_info_serial, date_time) ",
        "  WHERE device_info_serial=%s AND date_time BETWEEN '%s' AND '%s' ",
        "  AND longitude IS NOT NULL AND userflag<>1 ",
        "  GROUP BY date(date_time) ",
        ") a USING (date) ",
        # Add intervals
        "LEFT JOIN ( ",
        # cannot use group by and lag in same query so do nested query
        "  SELECT date(date_time) as date, date_part('epoch', min(gpsinterval)) as mingpsinterval, date_part('epoch', max(gpsinterval)) as maxgpsinterval ",
        "    FROM ( ",
        "    SELECT date_time, date_time - lag(date_time) over (order by device_info_serial, date_time) as gpsinterval ",
        "    FROM gps.ee_tracking_speed_limited ",
        "    WHERE device_info_serial=%s AND date_time BETWEEN '%s' AND '%s' ",
        "    AND longitude IS NOT NULL AND userflag<>1 ",
        "  ) ti ",
        "  GROUP BY date(date_time) ",
        " ) i USING (date) ",
        "ORDER BY date"
    , sep="")

    sql <- sprintf(tpl, spheroid,
                   TrackerIdentifier, startTime, stopTime,
                   TrackerIdentifier, startTime, stopTime,
                   TrackerIdentifier, startTime, stopTime,
                   TrackerIdentifier, startTime, stopTime
                   )

    results <- dbGetQuery(conn, sql)

    dbDisconnect(conn)

    # Save as text
    write.table(results, sep=",", row.names=FALSE, quote=FALSE, file=file.path(outputDir, "result.csv"))
}
