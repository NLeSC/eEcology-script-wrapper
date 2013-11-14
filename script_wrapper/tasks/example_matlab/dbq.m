function db_query(dbUsername, dbPassword, dbName, databaseHost, TrackerIdentifiers, startTime, stopTime)
% dbUsername is a string for connecting to the database
% dbPassword is a string for connecting to the database
% dbName is a string
% databaseHost is a string hostname of the database
% TrackerIdentifiers is a string representation of an array of tracker indentifiers, eg '[620,800]'.
% startTime is a string in ISO8601 time format, eg. '2013-07-01T00:00:00'
% stopTime is a string in ISO8601 time format, eg. '2013-07-01T00:00:00'

% This function uses the OpenEarth toolbox

close all

% Command to compile:
% mcc -mv -R -nodisplay -I openearth/io/postgresql -I openearth -I openearth/general -I openearth/general/io_fun dbq.m

% Usage:
% ./run_dbq.sh /opt/matlab2009b '****' '****' eecology db.e-ecology.sara.nl '[620,800]' 2010-07-01T00:00:00 2010-09-01T00:00:00

% Sometimes required to find postgresql driver
% pg_settings()

conn = pg_connectdb(dbName, 'host', databaseHost, 'user', dbUsername, 'pass', dbPassword);

% SV: Command line arguments are strings, use eval to convert them into Matlab variable types.
if ischar(TrackerIdentifiers)
  TrackerIdentifiers = eval(TrackerIdentifiers);
end

% The SQL IN statement requires a comma seperated list of track indentifiers
n=numel(TrackerIdentifiers);formatStr = [repmat('%d,',[1,n-1]),'%d'];
TrackerIdentifiersCommaJoined = sprintf(formatStr,TrackerIdentifiers)

sql = ['SELECT device_info_serial, count(*) ',...
       'FROM gps.uva_tracking_limited ',...
       'WHERE device_info_serial IN (',TrackerIdentifiersCommaJoined,') ',...
       'AND date_time BETWEEN ',char(39) , startTime,char(39) , ' AND ',char(39) , stopTime, char(39), ' ',...
       'GROUP BY device_info_serial'];
results = pg_fetch(conn, sql);
display(results);

save('results.mat','results')


