import json
import os
from celery.utils.log import get_task_logger
import colander
from sqlalchemy import func
from script_wrapper.tasks import PythonTask
from script_wrapper.models import DBSession, Speed
from script_wrapper.models import getGPSCount
from script_wrapper.validation import validateRange
from script_wrapper.validation import iso8601Validator

logger = get_task_logger(__name__)


class Schema(colander.MappingSchema):
    start = colander.SchemaNode(colander.String(), validator=iso8601Validator)
    end = colander.SchemaNode(colander.String(), validator=iso8601Validator)
    tracker_id = colander.SchemaNode(colander.Int())


class ExamplePython(PythonTask):
    name = 'examplepython'
    label = 'Example in Python'
    title = 'Title of example in Python'
    autoregister = False
    MAX_FIX_COUNT = 50000

    def run(self, db_url, tracker_id, start, end):
        # Perform a database query
        db_url = self.local_db_url(db_url)
        s = DBSession(db_url)()
        tid = Speed.device_info_serial
        dt = Speed.date_time
        q = s.query(tid, func.count(tid))
        q = q.filter(tid.in_(tracker_id))
        q = q.filter(dt.between(start, end))
        q = q.filter(Speed.userflag == 0)
        q = q.filter(Speed.longitude != None)
        q = q.group_by(tid)
        r = q.all()
        msg = json.dumps(r)

        s.close()

        # Write results to text files
        fn = os.path.join(self.output_dir(), 'result.txt')
        with open(fn, 'w') as f:
            f.write(msg)

        result = {}
        result['query'] = {'start': start,
                           'end': end,
                           'tracker_id': tracker_id,
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
