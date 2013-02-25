function gps_overview(username, password, dbname, dburl, query)
% clear all
% close all

% display(username);
% display(password);

% if ischar(KDevice)
%  KDevice = eval(KDevice);
%end

% display('KDevice');
% display(KDevice);
display('DB_PASSWORD');
display(getenv('DB_PASSWORD'));

% dbname = 'flysafe';
% dburl = 'jdbc:postgresql://localhost:5432/flysafe';

conn = database(dbname, username, password, 'org.postgresql.Driver',dburl);
setdbprefs('DataReturnFormat', 'cellarray');
res = fetch(conn, query);
display(query);
display(res);


