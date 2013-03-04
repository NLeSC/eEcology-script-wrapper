import tempfile
import os.path
from celery import Task
from celery import current_task
from celery.utils.log import get_task_logger
from trackertask.tasks import RTask

logger = get_task_logger(__name__)

class PlotR(RTask):
    name = "plotr"
    label = "Plot in R"
    description = """Perform something in R"""
    r_script = 'plot.r'

    def run(self, db_url, start, end, tracker_id):
        output_fn = os.path.join(self.output_dir, 'plot.svg')
        self.r.plotr(output_fn, tracker_id, start, end)
        return {'files': { 'plot.svg': output_fn}}

    def formfields2taskargs(self, fields, db_url):
        return {'start': fields['start'],
                'end': fields['end'],
                'tracker_id': fields['id'],
                # below example of adding argument values
                'db_url':  db_url,
                }
