import tempfile
import os.path
from celery import Task
from celery import current_task
from celery.utils.log import get_task_logger
import iso8601
from mako.template import Template
from script_wrapper.models import make_url
from script_wrapper.models import getGPSCount
from script_wrapper.tasks import RTask
from script_wrapper.validation import validateRange

logger = get_task_logger(__name__)


class Calendar(RTask):
    name = 'calendar'
    label = 'Calendar'
    description = 'Calendar heatmap with daily stats of tracker'
    script = 'calendar.r'
    autoregister = True

    def run(self, db_url, tracker_id, start, end):
        self.update_state(state="RUNNING")
        query = {'query': {'start': start,
                          'end': end,
                          'tracker_id': tracker_id,
                          }
                }

        u = make_url(db_url)

        # create csv
        self.r.calendar(u.username, u.password, u.database, u.host,
                        tracker_id, start.isoformat(), end.isoformat(), self.output_dir())

        # copy html
        tpl_fn = os.path.join(self.task_dir(), 'result.mak')
        tpl = Template(filename=tpl_fn)
        html_fn = os.path.join(self.output_dir(), 'result.html')
        html_f = file(html_fn, 'w')
        html = tpl.render(csv='result.csv', tracker_id=tracker_id, start=start, end=end)
        html_f.write(html)
        html_f.close()

        return query

    def formfields2taskargs(self, fields, db_url):
        start = iso8601.parse_date(fields['start'])
        end = iso8601.parse_date(fields['end'])
        tracker_id = fields['id']

        validateRange(getGPSCount(db_url, tracker_id, start, end), 0, 5000000)

        return {'start': start,
                'end': end,
                'tracker_id': tracker_id,
                # below example of adding argument values
                'db_url': db_url,
                }
