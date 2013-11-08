import os
import subprocess
from celery import Task
from celery import current_task
from celery.utils.log import get_task_logger
from script_wrapper.models import make_url
from script_wrapper.tasks import MatlabTask

logger = get_task_logger(__name__)

class ExampleMatlab(MatlabTask):
    name = 'examplematlab'
    label = 'Example in Matlab'
    description = 'Example in Matlab'
    """Perform a db query in a Matlab executable with postgresql query"""
    script = 'run_dbq.sh'
    autoregister = False
    matlab_version = '2009b'

    def run(self, db_url, trackers, start, end):
        u = make_url(db_url)
        db_name = self.sslify_dbname(u)

        # execute
        result = super(ExampleMatlab, self).run(u.username,
                                                u.password,
                                                db_name,
                                                u.host,
                                                self.list2vector_string(trackers),
                                                start,
                                                end,
                                                )

        result['query'] = {'start': start,
                           'end': end,
                           'trackers': trackers,
                           }

        return result

    def formfields2taskargs(self, fields, db_url):
        return {'start': fields['start'],
                'end': fields['end'],
                'trackers': fields['trackers'],
                # below example of adding argument values
                'db_url':  db_url,
                }
