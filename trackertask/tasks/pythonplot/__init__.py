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
import trackertask.models as models

logger = get_task_logger(__name__)

class PythonPlotTask(PythonTask):
    name = "pythonplot"
    label = "Plot in Python"
    description='Plots tracker measurements over time. By Stefan Verhoeven'

    """Perform a simple python task"""
    def run(self, start, end, trackers, username, password):
        ids = [tracker['id'] for tracker in trackers]
        msg = 'fancy plot of {} from {} to {}'.format(json.dumps(trackers), start, end)
        s = models.DBSession()
        tr = models.meta.tables['gps.uva_tracking_limited']
        tid = tr.columns.device_info_serial
        dt = tr.columns.date_time
        q = s.query(tid, func.count(tid))
        q = q.filter(tid.in_(ids))
        q = q.filter(dt.between(start, end))
        q = q.group_by(tid)
        r = q.all()
        msg += json.dumps(r)

        fn = os.path.join(self.output_dir, 'plot.txt')
        with open(fn, 'w') as f:
            f.write(msg)
        return { 'files': [{'path': fn, 'name': 'plot.txt', 'content_type': 'text/plain'
                }]}

    def formfields2taskargs(self, fields):
        return {'start': iso8601parse(fields['start']),
                'end': iso8601parse(fields['end']),
                'trackers': fields['trackers'],
                # below example of adding argument values
                'username': 'someuser',
                'password': 'somepw',
                }

def iso8601parse(datetime_string):
    return datetime.datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S"),
