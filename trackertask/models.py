import logging
import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.schema import CreateSchema

Base = declarative_base()

logger = logging.getLogger('trackertask')

GPS_SCHEMA = 'gps'

class Project(Base):
    __tablename__ = 'ee_project_limited'
    __table_args__ = {'schema': GPS_SCHEMA}

    key_name = Column(String, primary_key=True)
    common_name = Column(String)
    devices = relationship("Device", backref=backref('project'))
    individuals = relationship("Individual", backref=backref('project'))


class Device(Base):
    __tablename__ = 'ee_device_limited'
    __table_args__ = {'schema': GPS_SCHEMA}

    device_info_serial = Column(Integer, primary_key=True)
    project_key_name = Column(String, ForeignKey(Project.key_name))


class Individual(Base):
    __tablename__ = 'ee_individual_limited'
    __table_args__ = {'schema': GPS_SCHEMA}

    ring_number = Column(String, primary_key=True)
    species = Column(String)
    project_key_name = Column(String, ForeignKey(Project.key_name))


class TrackSession(Base):
    __tablename__ = 'ee_track_session_limited'
    __table_args__ = {'schema': GPS_SCHEMA}

    device_info_serial = Column(Integer,
                                ForeignKey(Device.device_info_serial),
                                primary_key=True,
                                )
    ring_number = Column(String,
                         ForeignKey(Individual.ring_number),
                         primary_key=True,
                         )

class Tracking(Base):
    __tablename__ = 'ee_tracking_limited'
    __table_args__ = {'schema': GPS_SCHEMA}

    device_info_serial = Column(Integer, primary_key=True)
    date_time = Column(DateTime)


def request_credentials(request):
    (method, auth) = request.environ['HTTP_AUTHORIZATION'].split(' ', 1)
    if method.lower() != 'basic':
        raise NotImplementedError('Can only request credentials from Basic Authentication')
    (username, password) = auth.strip().decode('base64').split(':', 1)
    return (username, password)

def db_url_from_request(request):
    settings = request.registry.settings
    (username, password) = request_credentials(request)
    db_url = make_url(settings['sqlalchemy.url'])
    if username is not None:
        db_url.username = username
    if password is not None:
        db_url.password = password
    return str(db_url)

def DBSession(db_url):
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session

def make_session_from_request(request):
    db_url = db_url_from_request(request)
    engine = create_engine(db_url, poolclass=NullPool)
    Session = sessionmaker(bind=engine)
    return Session

def populate(session):
    """

    Create db::

        sudo -u postgres createdb -O stefanv eecology

    In python shell::

        import trackertask.models as m
        u = 'postgresql://localhost/eecology?sslmode=require'
        Session = m.DBSession(u)
        session = Session()
        m.populate(session)
        Session.close_all()

    Grant other users select rights::

        GRANT USAGE ON SCHEMA gps TO public;
        GRANT SELECT ON TABLE gps.ee_device_limited_device_info_serial_seq TO public;
        GRANT SELECT ON TABLE gps.ee_tracking_limited_device_info_serial_seq TO public;
        GRANT SELECT ON TABLE gps.ee_device_limited TO public;
        GRANT SELECT ON TABLE gps.ee_individual_limited TO public;
        GRANT SELECT ON TABLE gps.ee_project_limited TO public;
        GRANT SELECT ON TABLE gps.ee_track_session_limited TO public;
        GRANT SELECT ON TABLE gps.ee_tracking_limited TO public;

    """
    engine = session.get_bind()
    # Create schema
    try:
        engine.execute(CreateSchema(GPS_SCHEMA))
    except ProgrammingError as e:
        if 'already exists' not in str(e):
            raise e
    # Create tables
    Base.metadata.create_all(engine)
    # Fill tables
    project = Project(key_name='TEST1', common_name='Test 1 project')
    session.add(project)
    for tid in range(1,10):
        device = Device(device_info_serial=tid)
        project.devices.append(device)
        rn = 'C-{}'.format(tid)
        individual = Individual(ring_number=rn,
                                species='Lesser Black-backed Gull',
                                )
        project.individuals.append(individual)
        session.flush()
        session.add(TrackSession(device_info_serial=tid,
                                 ring_number=rn,
                                 ))
        session.add(Tracking(device_info_serial=tid,
                             date_time=datetime.datetime.now()
                             ))
    session.commit()
