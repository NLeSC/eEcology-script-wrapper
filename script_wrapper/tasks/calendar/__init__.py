import colander
from celery.utils.log import get_task_logger
from script_wrapper.models import getGPSCount
from script_wrapper.tasks import RTask
from script_wrapper.validation import validateRange
from script_wrapper.validation import iso8601Validator

logger = get_task_logger(__name__)


class Schema(colander.MappingSchema):
    start = colander.SchemaNode(colander.String(), validator=iso8601Validator)
    end = colander.SchemaNode(colander.String(), validator=iso8601Validator)
    tracker_id = colander.SchemaNode(colander.Int())


class Calendar(RTask):
    name = 'calendar'
    label = 'Calendar'
    title = 'Calendar overview with daily statistics of GPS-tracker'
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
                        start, end,
                        self.output_dir())

        return query

    def formfields2taskargs(self, fields, db_url):
        schema = Schema()
        taskargs = schema.deserialize(fields)

        start = taskargs['start']
        end = taskargs['end']
        tracker_id = taskargs['tracker_id']
        validateRange(getGPSCount(db_url, tracker_id, start, end), 0, self.MAX_FIX_COUNT)

        taskargs['db_url'] = db_url
        return taskargs
