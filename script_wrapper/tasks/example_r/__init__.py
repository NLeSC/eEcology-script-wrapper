import os.path
from celery.utils.log import get_task_logger
from script_wrapper.tasks import RTask

logger = get_task_logger(__name__)


class ExampleR(RTask):
    name = 'exampler'
    label = 'Example in R'
    description = 'Example in R'
    script = 'dbq.r'
    autoregister = False

    def run(self, db_url, trackers, start, end):
        u = self.local_db_url(db_url)
        trackersInR = self.toIntVector(trackers)

        self.r.exampler(u.username, u.password, u.database, u.host,
                        trackersInR, start, end, self.output_dir())

        return {'query': {'start': start,
                          'end': end,
                          'trackers': trackers,
                          }
                }

    def formfields2taskargs(self, fields, db_url):
        return {'start': fields['start'],
                'end': fields['end'],
                'trackers': fields['trackers'],
                # below example of adding argument values
                'db_url': db_url,
                }
