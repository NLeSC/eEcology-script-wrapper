import time
import json
import os
from celery import Task
from celery import current_task
from celery import current_app
from trackertask.tasks import PythonTask

class PythonPlotTask(PythonTask):
    name = "pythonplot"
    label = "Plot in Python"
    description='Plots tracker measurements over time. By Stefan Verhoeven'

    """Perform a simple python task"""
    def run(self, start, end, tracker_id, username, password):
        for i in xrange(int(end)):
            current_task.update_state(state='PROGRESS',
                meta={'current': i, 'total': end})
            time.sleep(float(start))
        msg = 'fancy plot of {} from {} to {}'.format(tracker_id, start, end)
        fn = os.path.join(self.output_dir, 'plot.txt')
        with open(fn, 'w') as f:
            f.write(msg)
        return {'path': fn,
                'content_type': 'text/plain'
                }

    def formfields2taskargs(self, fields):
        return {'start': fields['start'],
                'end': fields['end'],
                'tracker_id': fields['id'],
                # below example of adding argument values
                'username': 'someuser',
                'password': 'somepw',
                }
