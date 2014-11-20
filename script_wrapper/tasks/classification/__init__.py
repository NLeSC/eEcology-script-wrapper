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
import iso8601
from script_wrapper.tasks import MatlabTask
from script_wrapper.models import getAccelerationCount
from script_wrapper.validation import validateRange

logger = get_task_logger(__name__)


class Classification(MatlabTask):
    name = 'classification'
    label = "Classification"
    title = """Classify accelerometer data of GPS-tracker"""
    script = 'run_classificator.sh'
    matlab_version = '2012a'
    autoregister = False
    MAX_ACC_COUNT = 50000

    def run(self, db_url, start, end, tracker_id, plot_accel):
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
        start = iso8601.parse_date(fields['start'])
        end = iso8601.parse_date(fields['end'])
        tracker_id = fields['id']
        plot_accel = fields['plot_accel']

        # Test if selection will give results
        validateRange(getAccelerationCount(db_url, tracker_id, start, end), 0, self.MAX_ACC_COUNT)

        return {'db_url':  db_url,
                'start': start,
                'end': end,
                'tracker_id': tracker_id,
                'plot_accel': plot_accel,
                }
