import tempfile
import os.path
from celery import Task
from celery import current_task
from trackertask.tasks import RTask

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

class PlotR(RTask):
    name = "plotr"
    label = "Plot in R"
    description = """Perform something in R"""
    r_script = 'plot.r'

    def run(self, start, end, tracker_id, username, password):
        output_fn = os.path.join(self.output_dir, 'plot.svg')
        self.r.plotr(output_fn, tracker_id, start, end)
        return {'files': { 'plot.svg': output_fn}}

    def formfields2taskargs(self, fields):
        return {'start': fields['start'],
                'end': fields['end'],
                'tracker_id': fields['id'],
                # below example of adding argument values
                'username': 'someuser',
                'password': 'somepw',
                }
