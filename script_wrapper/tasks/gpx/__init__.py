import mimetypes
import os
from celery.utils.log import get_task_logger
import colander
import iso8601
import gpxdata
from script_wrapper.tasks import PythonTask
from script_wrapper.models import DBSession, Speed, getGPSCount
from script_wrapper.validation import validateRange
from script_wrapper.validation import iso8601Validator

logger = get_task_logger(__name__)
# gpx is not known by mimetypes library, this will cause IE11 browser to open it, instead of save it
mimetypes.add_type('application/gpx+xml', '.gpx')

class Schema(colander.MappingSchema):
    start = colander.SchemaNode(colander.String(), validator=iso8601Validator)
    end = colander.SchemaNode(colander.String(), validator=iso8601Validator)
    tracker_id = colander.SchemaNode(colander.Int())


class Gpx(PythonTask):
    """Generate a GPX file for a track"""
    name = 'gpx'
    label = 'Flight Generator'
    title = 'Generate a GPX file for a track. Can be used in <a target="_new" href="http://www.doarama.com/">Doarama</a> visualization.'
    description = '''More information can be found <a target="_blank" href="https://services.e-ecology.sara.nl/wiki/index.php/Flight_Generator">here</a>.'''
    autoregister = True
    made_by_researcher = False
    MAX_FIX_COUNT = 50000

    def run(self, db_url, tracker_id, start, end):
        self.update_state(state="RUNNING")
        start = iso8601.parse_date(start)
        end = iso8601.parse_date(end)
        db_url = self.local_db_url(db_url)
        session = DBSession(db_url)()

        rows = self.query2rows(session, tracker_id, start, end)
        doc = self.track2gpx(tracker_id, rows)
        fn = self.getOutputFileName(tracker_id, start, end)
        doc.writeGPX(fn)

        session.close()

        result = {}
        result['query'] = {'start': start.isoformat(),
                           'end': end.isoformat(),
                           'tracker_id': tracker_id,
                           }
        return result

    def query2rows(self, session, tracker_id, start, end):
        # Perform a database query
        tid_col = Speed.device_info_serial
        dt_col = Speed.date_time
        q = session.query(dt_col,
                          Speed.longitude,
                          Speed.latitude,
                          Speed.altitude,
                          )
        q = q.filter(tid_col == tracker_id)
        q = q.filter(dt_col.between(start.isoformat(), end.isoformat()))
        q = q.filter(Speed.longitude != None)
        q = q.filter(Speed.latitude != None)
        q = q.filter(Speed.userflag == 0)
        q = q.order_by(dt_col)
        return q

    def track2gpx(self, tracker_id, rows):
        doc = gpxdata.Document([], 'eEcology')
        track = gpxdata.Track("Tracker " + str(tracker_id))
        trkseg = gpxdata.TrackSegment()
        for dt, lon, lat, alt in rows:
            point = gpxdata.Point(lat, lon, alt, dt)
            trkseg.append(point)
        track.append(trkseg)
        doc.append(track)
        return doc

    def getOutputFileName(self, tracker_id, start, end):
        filename_tpl = "s{start}-e{end}-t{id}.gpx"
        filename = filename_tpl.format(start=start.strftime('%Y%m%d%H%M'),
                                       end=end.strftime('%Y%m%d%H%M'),
                                       id=tracker_id,
                                       )
        fn = os.path.join(self.output_dir(), filename)
        return fn

    def formfields2taskargs(self, fields, db_url):
        schema = Schema()
        taskargs = schema.deserialize(fields)

        start = taskargs['start']
        end = taskargs['end']
        tracker_id = taskargs['tracker_id']
        validateRange(getGPSCount(db_url, tracker_id, start, end), 0, self.MAX_FIX_COUNT)

        taskargs['db_url'] = db_url
        return taskargs
