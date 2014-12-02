Install instructions
====================

Red hat 6/CentOS 6 dependencies
-------------------------------

  yum install postgresql-devel.x86_64 mod_perl ntp libXp java-1.6.0-openjdk

Octave, R, redis are available in epel repo::

  rpm -ivh http://mirror.1000mbps.com/fedora-epel/6/i386/epel-release-6-8.noarch.rpm
  yum install R redis octave
  chkconfig redis on
  /etc/init.d/redis start

Python-2.7 is needed for R integration, it is not-standard on rh6 so use compile it by hand.

As root::

  yum groupinstall "Development tools"
  yum install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel xz
  wget http://python.org/ftp/python/2.7.6/Python-2.7.6.tar.xz
  xz -d Python-2.7.6.tar.xz
  tar -xf Python-2.7.6.tar
  cd Python-2.7.6
  ./configure
  make
  make altinstall
  wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py
  python2.7 ez_setup.py
  wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py
  python2.7 get-pip.py
  pip install virtualenv

As application runner::

  cd $APPHOME
  virtualenv env
  . env/bin/activate
  python setup.py develop

Allow apache to reverse proxy and allow reading of static files in home dir with selinux::

  setsebool -P httpd_can_network_connect 1
  setsebool -P httpd_enable_homedirs true
  chcon -R -t httpd_user_content_t $APPHOME/trackertask/static

Appliction configuration
------------------------

  cp development.ini-dist development.ini

Or

  cp production.ini-dist production.ini

And edit it to fit needs.

Web application start/stop
--------------------------

Copy `extras/init/script-wrapper-web.conf` into `/etc/init/`.
Edit the application root and config filename variable.
Start with `start script-wrapper-web`.

Worker start/stop
-----------------

Copy `extras/init/script-wrapper-worker` into `/etc/init`.
Edit the application root and config filename variable.
Start with `start script-wrapper-worker`.

Monitoring web application and work
-----------------------------------

Nagios plugins are available in `extras/nagios`.

Apache configuration
--------------------

Create `/etc/httpd/conf.d/script-wrapper.conf` with following content or copy `extras/apache/script-wrapper-web.conf`::

  <Location /sw>
    AuthType basic
    AuthName "e-ecology credentials required"
    AuthBasicProvider file
    AuthUserFile /etc/httpd/script-wrapper.passwords
    Require valid-user
  </Location>

  ProxyPass /sw/static !
  ProxyPass /sw/ http://localhost:6543/sw/
  ProxyPassReverse /sw/ http://localhost:6543/sw/

  Alias /sw/static $APPHOME/trackertask/static

  <Directory $APPHOME/trackertask/static >
    Order allow,deny
    Allow from all
  </Directory>

Create `/etc/httpd/script-wrapper.passwords` with::

  htpasswd -c /etc/httpd/script-wrapper.passwords <username>

Enable it by

  chkconfig script-wrapper on
  /etc/init.d/script-wrapper start

Enable it by restarting apache with `/etc/init.d/httpd restart`.

See https://services.e-ecology.sara.nl/redmine/projects/uvagps/wiki/Apache_authentication_against_DB to add db authentication.

Script wrapper distributed workers
----------------------------------

To distribute work in cloud have one master machine with the web front-end and redis server.
Have multiple slaves with celery workers and local database. Script results will be shared over NFS.

1. Create cloud ubuntu machine with 25Gb disk.
2. Install dependencies
2.0 Update system + install git, build essentials + remove apache, add users myself+sw
2.1 NFS, /shared/Scratch/script-wrapper-sessions
2.2 postgresql + postgis
2.3 python, virtualenv
2.4 R, DBI, RPostgresql, stringr
2.5 Matlab MCR's
2.6 Octave
3. Install script-wrapper
3.1 Add ssh key to github + git clone
3.2 virtualenv, pip install numpy oct2py, python setup.py install
3.3 setup ini
3.4 add start/stop script

   description     "Script wrapper worker"

   start on (mounted MOUNTPOINT=/shared)
   stop on runlevel [!2345]

   setuid verhoes
   umask 022

   script
     cd /home/verhoes/eEcology-script-wrapper
     . env/bin/activate
     pceleryd development.ini
   end script

3.5 Redis server on master bind to all, open firewall `-A INPUT -i eth1 -j ACCEPT` for private network
4. Stop, rename template, start several instances.

Docker deployment
-----------------

Script wrapper consist of 3 container:
- web, instance of script-wrapper image
- redis
- worker, instance of script-wrapper image

Orchistration is done with fig (http://fig.sh).

1. Create docker image for script-wrapper
(Docker puts images in /var/lib/docker, this can be changed by starting docker deamon with `-g <graphdir>` option.)

    sudo docker build -t sverhoeven/eecology-script-wrapper:2.2.1 .
    sudo docker tag sverhoeven/eecology-script-wrapper:2.2.1 sverhoeven/eecology-script-wrapper:latest
    sudo docker login
    sudo docker push sverhoeven/eecology-script-wrapper:2.2.1
    sudo docker push sverhoeven/eecology-script-wrapper:latest

Or setup automated builds in docker registry hub, pushing commit will trigger a build. Version management needs to be done inside docker hub.

2. Setup jobs dir

    mkdir jobs
    chown www-data jobs

The script wrapper job results are shared between using the web and worker container using a host directory.
The `fig.yml` defaults to `jobs/` directory in current working directory.
Update `fig.yml` if jobs need to stored elsewhere.
The jobs dir should be writable by www-data (uid=33) user, as both web and worker service run as www-data user.

3. Start it, somewhere with docker(http://docker.com) and fig (http://fig.sh) installed

    fig -p script-wrapper up
