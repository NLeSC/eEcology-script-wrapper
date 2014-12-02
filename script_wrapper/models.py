# Copyright 2013 Netherlands eScience Center
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from os import environ
import logging
import datetime
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String, DateTime, Float, Binary
from sqlalchemy import create_engine
from sqlalchemy import func, cast, Numeric
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.schema import CreateSchema
from sqlalchemy.ext.hybrid import hybrid_property
from geoalchemy import GeometryColumn, Geometry, WKTSpatialElement
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql.expression import literal_column

Base = declarative_base()

logger = logging.getLogger('script_wrapper')

GPS_SCHEMA = 'gps'


class Tracker(Base):
    __tablename__ = 'ee_tracker_limited'
    __table_args__ = {'schema': GPS_SCHEMA}

    device_info_serial = Column(Integer, primary_key=True)


class Individual(Base):
    __tablename__ = 'ee_individual_limited'
    __table_args__ = {'schema': GPS_SCHEMA}

    ring_number = Column(String, primary_key=True)
    species = Column(String)


class TrackSession(Base):
    __tablename__ = 'ee_track_session_limited'
    __table_args__ = {'schema': GPS_SCHEMA}

    key_name = Column(String)
    device_info_serial = Column(Integer,
                                ForeignKey(Tracker.device_info_serial),
                                primary_key=True,
                                )
    ring_number = Column(String,
                         ForeignKey(Individual.ring_number),
                         primary_key=True,
                         )


class Speed(Base):
    __tablename__ = 'ee_tracking_speed_limited'
    __table_args__ = {'schema': GPS_SCHEMA}

    device_info_serial = Column(Integer, primary_key=True)
    date_time = Column(DateTime)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Integer)
    pressure = Column(Integer)
    temperature = Column(Float)
    satellites_used = Column(Integer)
    gps_fixtime = Column(Float)
    positiondop = Column(Float)
    h_accuracy = Column(Float)
    v_accuracy = Column(Float)
    x_speed = Column(Float)
    y_speed = Column(Float)
    z_speed = Column(Float)
    speed_accuracy = Column(Float)
    location = GeometryColumn(Geometry(2))
    # cannot use location in functions as it is wrapped by st_asbinary func as part of the geometry type
    rawlocation = Column('location', Binary)
    vnorth = Column(Float)
    veast = Column(Float)
    vdown = Column(Float)
    speed = Column(Float)
    speed3d = Column(Float)
    direction = Column(Float)
    userflag = Column(Integer)

    @hybrid_property
    def trajectDirection(self):
        """traject direction of previous location and current location"""
        azimuth = func.ST_Azimuth(func.lag(self.rawlocation).over(order_by=(self.device_info_serial, self.date_time,)), self.rawlocation)
        return func.round(cast(func.degrees(azimuth), Numeric()), 2).label('tdirection')

    @hybrid_property
    def trajectSpeed(self):
        """traject speed by distance between previous and current location divided by current date_time - previous date_time

        round(CAST
        (
            ST_Length_Spheroid(
                ST_MakeLine(location, lag(location) over (order by device_info_serial, date_time)),
                'SPHEROID[\"WGS 84\",6378137,298.257223563]'
            )
        /
        EXTRACT(
            EPOCH FROM (date_time - lag(date_time) over (order by device_info_serial, date_time))
        )
        ) AS NUMERIC, 4)
        """
        order_by = (self.device_info_serial, self.date_time,)
        spheroid = 'SPHEROID["WGS 84",6378137,298.257223563]'
        line = func.ST_MakeLine(self.rawlocation, func.lag(self.rawlocation).over(order_by=order_by))
        distance = func.ST_Length_Spheroid(line, spheroid)
        duration = func.extract('epoch', self.date_time - func.lag(self.date_time).over(order_by=order_by))
        return func.round(cast(distance / duration, Numeric), 4).label('tspeed')

    @hybrid_property
    def elevation(self):
        """returns subquery Terrain elevation based on srtm3/srtm30

        """
        # Tried to write as sqlalchemy, but subquery + array + geo made it not workable
        return literal_column("""coalesce(nullif(
                (
                SELECT max(the_data[floor(((st_ymax(bbox) - (st_y(location))) / abs(cellsize_y))+1)]
                         [floor(((st_x(location)- st_xmin(bbox)) / abs(cellsize_x))+1)])::float
                FROM elevation.srtm3
                WHERE bbox && location
                )
            , -9999
            )
            , (
            SELECT max(the_data[floor(((st_ymax(bbox) - (st_y(location))) / abs(cellsize_y))+1)]
                     [floor(((st_x(location)- st_xmin(bbox)) / abs(cellsize_x))+1)])::float
            FROM elevation.srtm30
            WHERE bbox && location
            )
        )
        """).label('elevation')


class Acceleration(Base):
    __tablename__ = 'ee_acceleration_limited'
    __table_args__ = {'schema': GPS_SCHEMA}

    key_name = Column(String)
    device_info_serial = Column(Integer, primary_key=True)
    date_time = Column(DateTime, primary_key=True)
    index = Column(Integer, primary_key=True)


class Energy(Base):
    __tablename__ = 'ee_energy_limited'
    __table_args__ = {'schema': GPS_SCHEMA}

    key_name = Column(String)
    device_info_serial = Column(Integer, primary_key=True)
    date_time = Column(DateTime, primary_key=True)
    vsll = Column(Float)
    vbat = Column(Float)
    ssw = Column(Integer)
    temperature = Column(Float)


class Elevation3(Base):
    __tablename__ = 'srtm3'
    __table_args__ = {'schema': 'elevation'}

    tid = Column(Integer, primary_key=True)
    bbox = GeometryColumn(Geometry())
    rawbbox = Column(Binary, name='bbox')
    cellsize_x = Column(Float)
    cellsize_y = Column(Float)
    the_data = Column(ARRAY(Integer, dimensions=2))


class Elevation30(Base):
    __tablename__ = 'srtm30'
    __table_args__ = {'schema': 'elevation'}

    tid = Column(Integer, primary_key=True)
    bbox = GeometryColumn(Geometry())
    rawbbox = Column(Binary, name='bbox')
    cellsize_x = Column(Float)
    cellsize_y = Column(Float)
    the_data = Column(ARRAY(Integer, dimensions=2))


def request_credentials(request):
    """Returns the username/password from the authorization header with Basic Authentication.

    When authorization header is missing it returns (None, None) tuple.
    """
    if 'HTTP_AUTHORIZATION' not in request.environ:
        logger.warn('No HTTP_AUTHORIZATION found, using empty credentials')
        return (None, None)
    (method, auth) = request.environ['HTTP_AUTHORIZATION'].split(' ', 1)
    if method.lower() != 'basic':
        err = 'Can only request credentials from Basic Authentication'
        raise NotImplementedError(err)
    (username, password) = auth.strip().decode('base64').split(':', 1)
    return (username, password)


def db_url_from_request(request):
    settings = request.registry.settings
    (username, password) = request_credentials(request)
    db_url = make_url(settings['sqlalchemy.url'])
    # make db host overwritable with DB_HOST environment variable
    db_url.host = environ.get('DB_HOST', db_url.host)
    if username:
        db_url.username = username
    if password:
        db_url.password = password
    return str(db_url)


def DBSession(db_url):
    """Returns sqlalchemy db session based on db_url
    eg.

        session = DBSession('postgresql://username:password@db.e-ecology.sara.nl/eecology?sslmode=require')

        # Do queries with session

        session.close()
    """
    engine = create_engine(db_url, poolclass=NullPool)
    Session = sessionmaker(bind=engine)
    return Session


def make_session_from_request(request):
    """Returns sqlalchemy db session based on pyramid request object"""
    db_url = db_url_from_request(request)
    Session = DBSession(db_url)
    return Session


def populate(session):
    """

    Install Postgresql server with PostGIS extension

    Create db::

        sudo -u postgres -i
        createdb -O stefanv eecology
        psql -d eecology -c "CREATE EXTENSION postgis;"

        # as yourself
        CREATE SCHEMA gps;
        CREATE SCHEMA elevation;
        -- Create elevation schema
        GRANT USAGE ON SCHEMA elevation TO public;
        CREATE OR REPLACE FUNCTION elevation.srtm_getvalue(IN my_point geometry, OUT altitude numeric)
          RETURNS numeric AS
        $BODY$
        SELECT -9999.0
        $BODY$
          LANGUAGE sql IMMUTABLE STRICT
          COST 100;

    In python shell::

        import script_wrapper.models as m
        u = 'postgresql://username:password@localhost/eecology?sslmode=require'
        Session = m.DBSession(u)
        session = Session()
        m.populate(session)
        Session.close_all()

    Grant other users select rights::

        GRANT USAGE ON SCHEMA gps TO public;
        GRANT SELECT ON TABLE gps.ee_tracker_limited_device_info_serial_seq TO public;
        GRANT SELECT ON TABLE gps.ee_tracker_limited TO public;
        GRANT SELECT ON TABLE gps.ee_individual_limited TO public;
        GRANT SELECT ON TABLE gps.ee_track_session_limited TO public;
        GRANT SELECT ON TABLE gps.ee_tracking_speed_limited TO public;
        GRANT SELECT ON TABLE gps.ee_tracking_acceleration_limited TO public;
        GRANT SELECT ON TABLE gps.ee_energy_limited TO public;

    Or to load a dump::

        # edit pg_hba.conf so md5 is needed for all local users + restart postgresql server
        # as postgres user
        initdb /datadir
        psql < roles.sql
        echo "ALTER USER eecology WITH PASSWORD '*****';" | psql
        echo "GRANT flysafe TO eecology GRANTED BY postgres;" |psql
        createdb -O eecology eecology
        createlang plpgsql eecology
        psql -d eecology -f /usr/share/postgresql/8.4/contrib/postgis-1.5/postgis.sql
        psql -d eecology -f /usr/share/postgresql/8.4/contrib/postgis-1.5/spatial_ref_sys.sql
        # as me
        screen
        gunzip -c elevation_dump.sql.gz | psql -U eecology -W eecology
        psql -U eecology -W eecology < gps.sql
        # edit dump.sql.gz so search_path includes public schema
        gunzip -c gps_dump.sql.gz | psql -U eecology -W eecology

        # sync rights
        # TODO 2 acces tables have been replaced with admin schema, dump and import admin schema
    """
    engine = session.get_bind()
    # Create schema
    try:
        engine.execute(CreateSchema(GPS_SCHEMA))
    except ProgrammingError as e:
        if 'already exists' not in str(e):
            raise e
    # Create tables
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    # Fill tables
    for tid in range(1, 10):
        tracker = Tracker(device_info_serial=tid)
        session.add(tracker)
        rn = 'C-{}'.format(tid)
        individual = Individual(ring_number=rn,
                                species='Lesser Black-backed Gull',
                                )
        session.add(individual)
        session.flush()
        session.add(TrackSession(device_info_serial=tid,
                                 ring_number=rn,
                                 key_name='Someone, someone@example.com'
                                 ))
        dt = datetime.datetime.utcnow()
        offset = tid * 0.1
        lon = 4.830617 + offset
        lat = 52.979970 + offset
        loc = WKTSpatialElement('POINT({} {})'.format(lon, lat))
        session.add(Speed(device_info_serial=tid,
                          date_time=dt,
                          longitude=lon,
                          latitude=lat,
                          location=loc,
                          speed=15,
                          direction=45,
                          ))
        session.add(Acceleration(device_info_serial=tid,
                                 date_time=dt,
                                 index=1,
                                 ))
        session.add(Energy(device_info_serial=tid,
                           date_time=dt,
                           vsll=0.009,
                           vbat=3.929,
                           ssw=63,
                           ))
    session.commit()


def getAccelerationCount(db_url, device_info_serial, start, end):
    """Returns the number of acceleration rows for selected tracker and time range.
    """
    s = DBSession(db_url)()
    q = s.query(func.count(Acceleration.device_info_serial))
    q = q.filter(Acceleration.device_info_serial == device_info_serial)
    q = q.filter(Acceleration.date_time.between(start.isoformat(),
                                                end.isoformat()))
    acount = q.scalar()
    s.close()
    return acount


def getGPSCount(db_url, device_info_serial, start, end):
    """Returns the number of gps rows for selected tracker and time range.
    """
    s = DBSession(db_url)()
    q = s.query(func.count(Speed.device_info_serial))
    q = q.filter(Speed.device_info_serial == device_info_serial)
    q = q.filter(Speed.date_time.between(start.isoformat(), end.isoformat()))
    q = q.filter(Speed.userflag == 0)
    gcount = q.scalar()
    s.close()
    return gcount
