Deployment
==========

Requirements
------------

Requires a http reverse proxy which does basic authentication and passes HTTP_AUTHENTICATION and HTTP_REMOTE_USER environment variables.
By default uses a redis store to communicate between web application (pserve) and workers (pceleryd) so requires a redis store.

ExtJS (http://www.sencha.com/products/extjs) is used as widget library. 
ExtJS should be extracted in `script_wrapper/static/ext` folder. 

  cd script_wrapper/static
  wget http://cdn.sencha.com/ext/gpl/ext-4.2.1-gpl.zip
  unzip ext-4.2.1-gpl.zip
  ln -s ext-4.2.1.883 ext

Installation
------------

To install the script wrapper::

  python setup.py develop
  cp development.ini-dist development.ini

Run
---

  pserve developement.ini
  # in other shell
  pceleryd development.ini

To run as daemons::

  pserve --daemon --log-file=error.log development.ini
  nohup pceleryd development.ini --pidfile=$PWD/worker.pid -f worker.log &

Matlab compile runtime
----------------------

Install same version as used to compile.

Add postgresql jdbc (/usr/share/java/postgresql-jdbc3.jar) to
~/MATLAB/MATLAB_Compiler_Runtime/v717/toolbox/local/classpath.txt

Java is missing, add by::

   cd /home/stefanv/MATLAB/MATLAB_Compiler_Runtime/v711/sys/
   mkdir -p java/jre
   ln -s /usr/lib/jvm/java-6-openjdk-amd64 java/jre/glnxa64


R
-

To query database install from R prompt:

  install.packages('RPostgreSQL')
  install.packages('stringr')

Add cert for postgresql jdbc ssl connection
-------------------------------------------

See http://jdbc.postgresql.org/documentation/91/ssl-client.html
