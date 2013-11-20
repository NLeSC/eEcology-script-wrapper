import json
import os
from celery.utils.log import get_task_logger
import iso8601
from sqlalchemy import func
from script_wrapper.tasks import PythonTask
from script_wrapper.models import DBSession, Tracking

logger = get_task_logger(__name__)


class ExamplePython(PythonTask):
    name = 'examplepython'
    label = 'Example in Python'
    description = 'Example in Python'
    autoregister = False

    def run(self, db_url, trackers, start, end):
        # Perform a database query
        s = DBSession(db_url)()
        tid = Tracking.device_info_serial
        dt = Tracking.date_time
        q = s.query(tid, func.count(tid))
        q = q.filter(tid.in_(trackers))
        q = q.filter(dt.between(start, end))
        q = q.group_by(tid)
        r = q.all()
        msg = json.dumps(r)

        s.close()

        # Write results to text files
        fn = os.path.join(self.output_dir(), 'result.txt')
        with open(fn, 'w') as f:
            f.write(msg)

        result = {}
        result['query'] = {'start': start,
                           'end': end,
                           'trackers': trackers,
                           }

        return result

    def formfields2taskargs(self, fields, db_url):
        return {'start': iso8601.parse_date(fields['start']),
                'end': iso8601.parse_date(fields['end']),
                'trackers': fields['trackers'],
                # below example of adding argument values
                'db_url': db_url,
                }
