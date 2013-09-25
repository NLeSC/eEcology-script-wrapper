exampler <- function(dbUsername, dbPassword, dbName, databaseHost, TrackerIdentifiers, startTime, stopTime, outputDir) {
    # Run in R with:
    # source('dbq.r')
    # exampler('****', '****, 'eecology', 'eecology db.e-ecology.sara.nl', c(620,800), '2010-07-01T00:00:00', '2010-09-01T00:00:00', '/tmp')
    library(RPostgreSQL)
    library(stringr)
    drv <- dbDriver("PostgreSQL")
    conn = dbConnect(drv, user=dbUsername, password=dbPassword, dbname=dbName, host=databaseHost)

    TrackerIdentifiersCommaJoined <- str_c(TrackerIdentifiers, collapse=",")

    sql <- paste("SELECT device_info_serial, count(*) FROM gps.uva_tracking_limited ",
       "WHERE device_info_serial IN (",TrackerIdentifiersCommaJoined, ") ",
       "AND date_time BETWEEN '", startTime,"' AND '",stopTime, "'",
       "GROUP BY device_info_serial")

    results <- dbGetQuery(conn, sql)

    # Save as text
    dump('results', file=file.path(outputDir, "results.txt"))
    # Save in R format
    save('results', file=file.path(outputDir, "results.rData"))
}
