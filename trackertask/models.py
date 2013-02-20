from sqlalchemy import MetaData
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

DBSession = scoped_session(sessionmaker())
meta = MetaData()

def reflect(bind, schema):
    """Perform relection on bind with schema

    Fills meta.tables dict.
    """
    return meta.reflect(bind=bind, schema=schema, views=True)

def trackers():
    session = DBSession()
    t = meta.tables
    trackers = []
    for tracker in session.query(t['gps.uva_device_limited']):
        trackers.append({'id': tracker.device_info_serial})
    return { 'trackers': trackers, 'total': len(trackers)}
