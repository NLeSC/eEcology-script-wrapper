import colander
from celery.utils.log import get_task_logger
from script_wrapper.models import getGPSCount
from script_wrapper.tasks import MatlabTask
from script_wrapper.validation import validateRange
from script_wrapper.validation import iso8601Validator

logger = get_task_logger(__name__)


class Schema(colander.MappingSchema):
    start = colander.SchemaNode(colander.String(), validator=iso8601Validator)
    end = colander.SchemaNode(colander.String(), validator=iso8601Validator)
    tracker_id = colander.SchemaNode(colander.Int())


class ExampleMatlab(MatlabTask):
    name = 'examplematlab'
    label = 'Example in Matlab'
    title = 'Example in Matlab'
    description = """Performs a db query in a Matlab executable with postgresql query"""
    script = 'run_dbq.sh'
    autoregister = False
    matlab_version = '2012b'

    def run(self, db_url, tracker_id, start, end):
        u = self.local_db_url(db_url)
        db_name = self.sslify_dbname(u)

        # execute
        result = super(ExampleMatlab, self).run(u.username,
                                                u.password,
                                                db_name,
                                                u.host,
                                                self.list2vector_string([tracker_id]),
                                                start,
                                                end,
                                                )

        result['query'] = {'start': start,
                           'end': end,
                           'tracker': tracker_id,
                           }

        return result

    def formfields2taskargs(self, fields, db_url):
        schema = Schema()
        taskargs = schema.deserialize(fields)

        start = taskargs['start']
        end = taskargs['end']
        tracker_id = taskargs['tracker_id']
        validateRange(getGPSCount(db_url, tracker_id, start, end), 0, self.MAX_FIX_COUNT)

        taskargs['db_url'] = db_url
        return taskargs
