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

import unittest
from mock import patch
from script_wrapper.tasks.example_python import ExamplePython


class TestExamplePython(unittest.TestCase):

    @patch('script_wrapper.tasks.example_python.getGPSCount')
    def test_formfields2taskargs(self, gpscount):
        gpscount.return_value = 400
        task = ExamplePython()

        formquery = {'tracker_id': 1234,
                     'start': '2013-01-01T00:00:00',
                     'end': '2013-10-10T00:00:00',
                     }

        taskargs = task.formfields2taskargs(formquery,
                                            'postgresql://localhost')

        etaskargs = {'db_url': 'postgresql://localhost',
                     'tracker_id': 1234,
                     'start': '2013-01-01T00:00:00',
                     'end': '2013-10-10T00:00:00',
                     }

        self.assertEqual(taskargs, etaskargs)
