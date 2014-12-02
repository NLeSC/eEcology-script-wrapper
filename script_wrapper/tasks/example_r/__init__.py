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


class ExampleR(RTask):
    name = 'exampler'
    label = 'Example in R'
    title = 'Title of example in R'
    script = 'dbq.r'
    autoregister = False

    def run(self, db_url, tracker_id, start, end):
        u = self.local_db_url(db_url)
        trackersInR = self.toIntVector([tracker_id])

        self.r.exampler(u.username, u.password, u.database, u.host,
                        trackersInR, start, end, self.output_dir())

        return {'query': {'start': start,
                          'end': end,
                          'tracker_id': tracker_id,
                          }
                }

    def formfields2taskargs(self, fields, db_url):
        schema = Schema()
        taskargs = schema.deserialize(fields)

        start = taskargs['start']
        end = taskargs['end']
        tracker_id = taskargs['tracker_id']
        validateRange(getGPSCount(db_url, tracker_id, start, end), 0, self.MAX_FIX_COUNT)

        taskargs['db_url'] = db_url
        return taskargs
