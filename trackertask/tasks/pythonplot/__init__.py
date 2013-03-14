import time
import json
import os
import datetime
from celery import Task
from celery import current_task
from celery import current_app
from celery.utils.log import get_task_logger
from sqlalchemy import func
from trackertask.tasks import PythonTask
from trackertask.models import DBSession, Tracking

logger = get_task_logger(__name__)

class PythonPlotTask(PythonTask):
    name = "pythonplot"
    label = "Plot in Python"
    description='Plots tracker measurements over time. By Stefan Verhoeven'

    """Perform a simple python task"""
    def run(self, db_url, start, end, trackers):
        ids = [tracker['id'] for tracker in trackers]
        msg = 'fancy plot of {0} from {1} to {2}'.format(json.dumps(trackers), start, end)
        s = DBSession(db_url)
        tid = Tracking.device_info_serial
        dt = Tracking.date_time
        q = s().query(tid, func.count(tid))
        q = q.filter(tid.in_(ids))
        q = q.filter(dt.between(start, end))
        q = q.group_by(tid)
        r = q.all()
        msg += json.dumps(r)

        s.close_all();

        fn = os.path.join(self.output_dir, 'plot.txt')
        with open(fn, 'w') as f:
            f.write(msg)
        return {'files': {'plot.txt': fn}}

    def formfields2taskargs(self, fields, db_url):
        return {'start': iso8601parse(fields['start']),
                'end': iso8601parse(fields['end']),
                'trackers': fields['trackers'],
                # below example of adding argument values
                'db_url': db_url,
                }

def iso8601parse(datetime_string):
    return datetime.datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S")
