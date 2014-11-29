FROM ubuntu:14.04
MAINTAINER Stefan Verhoeven "s.verhoeven@esciencecenter.nl"
ENV DB_HOST db.e-ecology.sara.nl
ENV PYTHON_EGG_CACHE /tmp
EXPOSE 6543
VOLUME /jobs
RUN apt-get update
RUN apt-get install -y python-dev python-virtualenv wget libpq-dev

# Octave
RUN apt-get install -y octave python-numpy python-scipy

# Install Matlab runtime environment


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
RUN cd script_wrapper/static && wget http://cdn.sencha.com/ext/gpl/ext-4.2.1-gpl.zip && unzip ext-4.2.1-gpl.zip &&  ln -s ext-4.2.1.883 ext

RUN python setup.py develop

CMD gunicorn --env DB_HOST=$DB_HOST --paste production.ini-docker

