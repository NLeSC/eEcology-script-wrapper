import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import make_url

Base = declarative_base()

logger = logging.getLogger('trackertask')


class Projects(Base):
    __tablename__ = 'ee_project_limited'
    __table_args__ = {'schema':'gps'}

    key_name = Column(String, primary_key=True)
    common_name = Column(String)


class Devices(Base):
    __tablename__ = 'ee_device_limited'
    __table_args__ = {'schema':'gps'}

    device_info_serial = Column(Integer, primary_key=True)
    project_key_name = Column(String, ForeignKey(Projects.key_name))


class Individuals(Base):
    __tablename__ = 'ee_individual_limited'
    __table_args__ = {'schema':'gps'}

    ring_number = Column(String, primary_key=True)
    species = Column(String)
    project_key_name = Column(String, ForeignKey(Projects.key_name))


class TrackSession(Base):
    __tablename__ = 'ee_track_session_limited'
    __table_args__ = {'schema':'gps'}

    device_info_serial = Column(Integer,
                                ForeignKey(Devices.device_info_serial),
                                primary_key=True,
                                )
    ring_number = Column(String,
                         ForeignKey(Individuals.ring_number),
                         primary_key=True,
                         )

class Trackings(Base):
    __tablename__ = 'ee_tracking_limited'
    __table_args__ = {'schema':'gps'}

    device_info_serial = Column(Integer, primary_key=True)
    date_time = Column(DateTime)


def request_credentials(request):
    (method, auth) = request.environ['HTTP_AUTHORIZATION'].split(' ', 1)
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
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session

def populate(session):
    """

    Create db::

        sudo -u postgres createdb -O stefanv flysafe


    In python shell::

        import trackertask.models as m
        u = 'postgresql://localhost/flysafe?sslmode=require'
        Session = m.make_session(u)
        m.populate(Session())

    """
    engine = session.get_bind()
    Base.metadata.create_all(engine)
    for tid in range(1,10):
        session.add(Devices(device_info_serial=tid,
                            ))
        rn = 'C-{}'.format(tid)
        session.add(Individuals(ring_number=rn,
                                species='Lesser Black-backed Gull',
                                project_leader='Chris Thaxter',
                                ))
        session.add(TrackSession(device_info_serial=tid,
                                 ring_number=rn,
                                 ))
    session.commit()
