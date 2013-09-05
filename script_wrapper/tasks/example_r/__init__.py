import tempfile
import os.path
from celery import Task
from celery import current_task
from celery.utils.log import get_task_logger
from script_wrapper.models import make_url
from script_wrapper.tasks import iso8601parse
from script_wrapper.tasks import RTask

logger = get_task_logger(__name__)

class ExampleR(RTask):
    name = 'exampler'
    label = 'Example in R'
    description = 'Example in R'
    r_script = 'plot.r'
    auto_register = False

    def run(self, db_url, start, end, trackers):
        u = make_url(db_url)
        self.r.plotr(u.username, u.password, u.database, u.host , trackers, start, end)
        return {}

    def formfields2taskargs(self, fields, db_url):
        return {'start': iso8601parse(fields['start']),
                'end': iso8601parse(fields['end']),
                'trackers': fields['trackers'],
                # below example of adding argument values
                'db_url': db_url,
                }
