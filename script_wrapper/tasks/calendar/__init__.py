import os.path
from celery.utils.log import get_task_logger
import iso8601
from script_wrapper.models import getGPSCount
from script_wrapper.tasks import RTask
from script_wrapper.validation import validateRange

logger = get_task_logger(__name__)


class Calendar(RTask):
    name = 'calendar'
    label = 'Calendar'
    description = 'Calender overview with daily statistics of GPS-tracker'
    script = 'calendar.r'
    result_template = 'result.mak'
    autoregister = True
    made_by_researcher = False
    MAX_FIX_COUNT = 1000000

    def run(self, db_url, tracker_id, start, end):
        self.update_state(state="RUNNING")
        query = {'query': {'start': start,
                          'end': end,
                          'tracker_id': tracker_id,
                          }
                }

        u = self.local_db_url(db_url)

        # create csv
        self.r.calendar(u.username, u.password, u.database, u.host,
                        tracker_id,
                        start.isoformat(), end.isoformat(),
                        self.output_dir())

        return query

    def formfields2taskargs(self, fields, db_url):
        start = iso8601.parse_date(fields['start'])
        end = iso8601.parse_date(fields['end'])
        tracker_id = fields['id']

        validateRange(getGPSCount(db_url, tracker_id, start, end), 0, self.MAX_FIX_COUNT)

        return {'start': start,
                'end': end,
                'tracker_id': tracker_id,
                # below example of adding argument values
                'db_url': db_url,
                }
