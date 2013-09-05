plotr <- function(dbUsername, dbPassword, dbName, databaseHost, TrackerIdentifiers, startTime, stopTime) {

    library(RPostgresSQL)
    conn = dbConnect(PostgreSQL(), user= dbUsername, password=dbPassword, dbname=dbName, host=datebaseHost)

    library(RSvgDevice)
    devSVG(file=output_file)
    plot(c(1, 3, 6, 4, 9), type="o", col="blue", main=title, xlab=start, ylab=end)
    dev.off()
}
