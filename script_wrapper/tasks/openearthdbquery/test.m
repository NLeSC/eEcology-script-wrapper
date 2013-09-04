function testdb(dbname, host, username, password)

% mcc -mv -I openearth/io/postgresql -I openearth -I openearth/general -I openearth/general/io_fun test.m
% mcc -mv -I openearth/io/postgresql test.m
% addpath('openearth/io/postgresql')
% addpath('openearth')
% addpath('openearth/general')
% addpath('openearth/general/io_fun')

% pg_settings()

conn = pg_connectdb(dbname, 'host', host, 'user', username, 'pass', password, 'database_toolbox', 0);

res = pg_fetch(conn, 'SELECT * FROM gps.uva_individual');

display(res);
