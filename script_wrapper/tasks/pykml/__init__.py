import time
import json
import os
from celery import Task
from celery import current_task
from celery import current_app
from celery.utils.log import get_task_logger
import iso8601
from sqlalchemy import func
import simplekml
from script_wrapper.tasks import PythonTask
from script_wrapper.models import DBSession, Tracking, getGPSCount
from script_wrapper.validation import validateRange

logger = get_task_logger(__name__)


class PyKML(PythonTask):
    name = 'PyKML'
    label = 'Generate KML file'
    description = 'Using python'
    autoregister = False

    def run(self, db_url, tracker_id, start, end):
        # Perform a database query
        s = DBSession(db_url)
        tid = Tracking.device_info_serial
        dt = Tracking.date_time
        q = s().query(Tracking)
        q = q.filter(tid == tracker_id)
        q = q.filter(dt.between(start, end))

        kml = simplekml.Kml(open=1)

        style = simplekml.Style()

        for row in q:
            pnt = kml.newpoint()
            pnt.style = style
            pnt.name = ''
            pnt.description = '<ul><li>UTC Time: {}</li><li>ID: {}</li></ul>'.format(row.date_time, row.device_info_serial)
            pnt.timestamp.when = row.date_time
            pnt.coord = [row.longitude, row.latitude, row.altitude]

        fn = os.path.join(self.output_dir(), 'result.kmz')
        kml.savekmz(fn)

        result = {}
        result['query'] = {'start': start,
                           'end': end,
                           'tracker_id': tracker_id,
                           }

        return result

    def formfields2taskargs(self, fields, db_url):
        start = iso8601.parse_date(fields['start'])
        end = iso8601.parse_date(fields['end'])
        tracker_id = fields['id']

        # Test if selection will give results
        validateRange(getGPSCount(db_url, tracker_id, start, end), 0, 50000)

        return {'db_url':  db_url,
                'start': start,
                'end': end,
                'tracker_id': tracker_id,
                }
