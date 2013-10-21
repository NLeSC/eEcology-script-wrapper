import inspect
import os
import subprocess
from celery import Task
from celery import current_task
from celery.utils.log import get_task_logger
from script_wrapper.tasks import MatlabTask
from script_wrapper.tasks import iso8601parse
from script_wrapper.models import make_url

logger = get_task_logger(__name__)


class Classification(MatlabTask):
    name = 'classification'
    label = "Classification"
    description = """Classify behavior of track"""
    script = 'run_classificator.sh'

    def run(self, db_url, start, end, tracker_id):
        u = make_url(db_url)

        db_name = u.database
        if 'sslmode' in u.query and u.query['sslmode'] in ['require', 'verify', 'verify-full']:
            db_name += '?ssl=true&sslfactory=org.postgresql.ssl.NonValidatingFactory'

        # Data directory, classification requires a classification model
        data_dir = os.path.dirname(os.path.abspath(inspect.getsourcefile(Classification)))

        # execute
        result = super(Classification, self).run(u.username,
                                                 u.password,
                                                 db_name,
                                                 u.host,
                                                 str(tracker_id),
                                                 start.isoformat(),
                                                 end.isoformat(),
                                                 data_dir,
                                                 )

        for fn in os.listdir(self.output_dir):
            result['files'][fn] = os.path.join(self.output_dir, fn)
        return result

    def formfields2taskargs(self, fields, db_url):
        return {'db_url':  db_url,
                'start': iso8601parse(fields['start']),
                'end': iso8601parse(fields['end']),
                'tracker_id': fields['id'],
                }
