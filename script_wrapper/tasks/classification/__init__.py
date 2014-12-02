# Copyright 2013 Netherlands eScience Center
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import inspect
import os
from celery.utils.log import get_task_logger
import colander
import iso8601
from script_wrapper.tasks import MatlabTask
from script_wrapper.models import getAccelerationCount
from script_wrapper.validation import validateRange
from script_wrapper.validation import iso8601Validator

logger = get_task_logger(__name__)


class Schema(colander.MappingSchema):
    start = colander.SchemaNode(colander.String(), validator=iso8601Validator)
    end = colander.SchemaNode(colander.String(), validator=iso8601Validator)
    tracker_id = colander.SchemaNode(colander.Int())
    plot_accel = colander.SchemaNode(colander.Boolean(), missing=False)


class Classification(MatlabTask):
    name = 'classification'
    label = "Classification"
    title = """Classify accelerometer data of GPS-tracker"""
    script = 'run_classificator.sh'
    matlab_version = '2012a'
    autoregister = False
    MAX_ACC_COUNT = 50000

    def run(self, db_url, start, end, tracker_id, plot_accel):
        start = iso8601.parse_date(start)
        end = iso8601.parse_date(end)
        u = self.local_db_url(db_url)
        db_name = self.sslify_dbname(u)

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
                                                 str(plot_accel).lower()
                                                 )

        result['query'] = {'start': start,
                           'end': end,
                           'tracker_id': tracker_id,
                           }

        return result

    def formfields2taskargs(self, fields, db_url):
        schema = Schema()
        taskargs = schema.deserialize(fields)

        # Test if selection will give results
        validateRange(getAccelerationCount(db_url,
                                           taskargs['tracker_id'],
                                           taskargs['start'],
                                           taskargs['end'],
                                           ), 0, self.MAX_ACC_COUNT)

        taskargs['db_url'] = db_url
        return taskargs
