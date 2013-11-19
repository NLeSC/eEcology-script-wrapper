calendar <- function(dbUsername, dbPassword, dbName, databaseHost, TrackerIdentifier, startTime, stopTime, outputDir) {
    # Run in R with:
    # source('dbq.r')
    # calendar('****', '****, 'eecology', 'eecology db.e-ecology.sara.nl', 620, '2010-07-01T00:00:00', '2010-09-01T00:00:00', '/tmp')
    library(RPostgreSQL)
    drv <- dbDriver("PostgreSQL")
    conn = dbConnect(drv, user=dbUsername, password=dbPassword, dbname=dbName, host=databaseHost)

    spheroid = 'SPHEROID["WGS 84",6378137,298.257223563]'

    # distance from http://gis.stackexchange.com/questions/19369/total-great-circle-distance-along-a-path-of-points-postgis
    tpl <- paste("SELECT to_char(date(date_time), 'YYYY-MM-DD') as date, ",
       " count(*) as fixes, ",
       " sum(nraccs) as accels, ",
       " round((ST_Length_Spheroid(ST_MakeLine(location),'%s')/1000.0)::numeric, 3) AS distance, ",
       " max(altitude) as maxalt, ",
       " round(avg(altitude)::numeric, 2) as avgalt, ",
       " min(altitude) as minalt, ",
       " max(temperature) as maxtemp, ",
       " round(avg(temperature)::numeric, 2) as avgtemp, ",
       " min(temperature) as mintemp ",
       "FROM gps.uva_tracking_limited ",
       "LEFT JOIN ( ",
       "  SELECT device_info_serial, date_time, count(*) as nraccs FROM gps.uva_acceleration_limited ",
       "  GROUP BY device_info_serial, date_time ",
       "  ) a USING (device_info_serial, date_time) ",
       "WHERE device_info_serial=%s ",
       "AND date_time BETWEEN '%s' AND '%s' ",
       "AND longitude IS NOT NULL AND userflag<>1 ",
       "GROUP BY date(date_time) ",
       "ORDER BY date(date_time) ", sep="")

    sql <- sprintf(tpl, spheroid, TrackerIdentifier, startTime, stopTime)

    results <- dbGetQuery(conn, sql)

    dbDisconnect(conn)

    # Save as text
    write.table(results, sep=",", row.names=FALSE, quote=FALSE, file=file.path(outputDir, "result.csv"))
}
