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

Python-2.7 is needed for R integration, it is not-standard on rh6 so use a repo.
See http://developerblog.redhat.com/2013/02/14/setting-up-django-and-python-2-7-on-red-hat-enterprise-6-the-easy-way/

As root::

  sh -c 'wget -qO- http://people.redhat.com/bkabrda/scl_python27.repo >> /etc/yum.repos.d/scl.repo'
  yum install python27

As application runner::

  scl enable python27 bash
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

And edit it to fit needs.

Web application start/stop
--------------------------

Copy `extras/init.d/script-wrapper` into `/etc/init.d/`.
Edit the application root and config filename variable.
Start with `/etc/init.d/script-wrapper start`.
Start during boot with `chkconfig script-wrapper on`.

Worker start/stop
-----------------

Copy `extras/init.d/script-wrapper-worker` into `/etc/init.d`.
Edit the application root and config filename variable.
Start with `/etc/init.d/script-wrapper-worker start`.
Start during boot with `chkconfig script-wrapper-worker on`.

Apache configuration
--------------------

Create `/etc/httpd/conf.d/script-wrapper.conf` with following content::

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
