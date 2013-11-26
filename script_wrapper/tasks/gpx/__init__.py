import os
from celery.utils.log import get_task_logger
import iso8601
import simplekml
from script_wrapper.tasks import PythonTask
from script_wrapper.models import DBSession, Speed, getGPSCount
from script_wrapper.validation import validateRange
import gpxdata

logger = get_task_logger(__name__)


class Gpx(PythonTask):
    """Generate a GPX file for a track"""
    name = 'gpx'
    label = 'GPX file'
    description = 'Generate a GPX file for a track.'
    autoregister = True
    MAX_FIX_COUNT = 50000

    def run(self, db_url, tracker_id, start, end):
        self.update_state(state="RUNNING")
        db_url = self.local_db_url(db_url)
        session = DBSession(db_url)()


        filename_tpl = "{start}-{end}-{id}.gpx"
        filename = filename_tpl.format(start=start,
                                       end=end,
                                       id=tracker_id,
                                       )
        fn = os.path.join(self.output_dir(), filename)
        doc = gpxdata.Document([], 'eEcology')
        self.track2gpx(doc, session, tracker_id, start, end)
        doc.writeGPX(fn)

        result = {}
        result['query'] = {'start': start.isoformat(),
                           'end': end.isoformat(),
                           'tracker_id': tracker_id,
                           }
        return result

    def track2gpx(self, doc, session, tracker_id, start, end):
        # Perform a database query
        tid = Speed.device_info_serial
        dt = Speed.date_time
        q = session.query(tid, dt,
                          Speed.longitude,
                          Speed.latitude,
                          Speed.altitude,
                          )
        q = q.filter(tid == tracker_id)
        q = q.filter(dt.between(start, end))
        q = q.filter(Speed.longitude != None)
        q = q.filter(Speed.direction != None)
        q = q.order_by(dt)

        track = gpxdata.Track("Tracker "+str(tracker_id))
        trkseg = gpxdata.TrackSegment()
        for tid, dt, lon, lat, alt in q.all():
            point = gpxdata.Point(lat,lon, alt, dt)
            trkseg.append(point)
        track.append(trkseg)
        doc.append(track)

    def formfields2taskargs(self, fields, db_url):
        start = iso8601.parse_date(fields['start'])
        end = iso8601.parse_date(fields['end'])
        tracker_id = fields['id']

        validateRange(getGPSCount(db_url, tracker_id, start, end), 0, self.MAX_FIX_COUNT)

        return {'db_url':  db_url,
                'start': start,
                'end': end,
                'tracker_id': tracker_id,
                }
