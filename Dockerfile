FROM ubuntu:14.04
MAINTAINER Stefan Verhoeven "s.verhoeven@esciencecenter.nl"
ENV DB_HOST db.e-ecology.sara.nl
# when starting celery as non-root it tries to write to /root/.egg_cache, redirect it to writeable location
ENV PYTHON_EGG_CACHE /tmp
EXPOSE 6543
RUN apt-get update
RUN apt-get install -y python-dev python-virtualenv wget libpq-dev unzip

# Octave
RUN apt-get install -y octave python-numpy python-scipy

# Install Matlab runtime environment
# remote server is very slow so download mcr outsite Dockerfile with
# wget http://nl.mathworks.com/supportfiles/MCR_Runtime/R2012a/MCR_R2012a_glnxa64_installer.zip
COPY MCR_R2012a_glnxa64_installer.zip /tmp/
RUN mkdir /tmp/mcr-install && cd /tmp/mcr-install && unzip ../MCR_R2012a_glnxa64_installer.zip && ./install -mode silent -agreeToLicense yes -destinationFolder /opt/MATLAB/MATLAB_Compiler_Runtime && cd /tmp && rm -rf mcr-install

# R
RUN apt-get install -y r-base-dev littler
# R packages
RUN /usr/share/doc/littler/examples/install.r DBI RPostgreSQL stringr && rm -rf /tmp/downloaded_packages/ /tmp/*.rds

# Install app
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install -r requirements.txt

COPY . /usr/src/app

# ExtJS
RUN cd script_wrapper/static && wget http://cdn.sencha.com/ext/gpl/ext-4.2.1-gpl.zip && unzip ext-4.2.1-gpl.zip && ln -s ext-4.2.1.883 ext && rm -f ext-4.2.1-gpl.zip

RUN python setup.py develop
# one python package was installed with -rw------- permission, so service can not be started as www-data user
#RUN chmod -R +r /usr/local/lib/python2.7/dist-packages/python_dateutil-2.2-py2.7.egg/EGG-INFO

CMD gunicorn --user www-data --env DB_HOST=$DB_HOST --paste production.ini-docker
