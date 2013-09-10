import tempfile
import os.path
from celery import Task
from celery import current_task
from celery.utils.log import get_task_logger
from script_wrapper.models import make_url
from script_wrapper.tasks import RTask

logger = get_task_logger(__name__)

class ExampleR(RTask):
    name = 'exampler'
    label = 'Example in R'
    description = 'Example in R'
    script = 'dbq.r'

    def run(self, db_url, trackers, start, end):
        u = make_url(db_url)
        trackersInR = self.toIntVector(trackers)
        self.r.exampler(u.username, u.password, u.database, u.host, trackersInR, start, end, self.output_dir)
        return {'files': self.outputFiles()}

    def formfields2taskargs(self, fields, db_url):
        return {'start': fields['start'],
                'end': fields['end'],
                'trackers': fields['trackers'],
                # below example of adding argument values
                'db_url': db_url,
                }
