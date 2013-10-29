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

from datetime import datetime
import unittest
from mock import patch
from script_wrapper.validation import Invalid
from script_wrapper.tasks.classification import Classification


class TestClassification(unittest.TestCase):

    @patch('script_wrapper.tasks.classification.getAccelerationCount')
    def test_formfields2taskargs(self, gac):
        gac.return_value = 10000
        task = Classification()

        formquery = {
                     'id': 1234,
                     'start': '2013-01-01T00:00:00',
                     'end': '2013-10-10T00:00:00',
                     }

        taskargs = task.formfields2taskargs(formquery,
                                            'postgresql://localhost')

        etaskargs = {
                     'db_url': 'postgresql://localhost',
                     'start': datetime(2013, 1, 1),
                     'end': datetime(2013, 10, 10),
                     'tracker_id': 1234,
                     }

        self.assertEqual(taskargs, etaskargs)

    @patch('script_wrapper.tasks.classification.getAccelerationCount')
    def test_formfields2taskargs_invalid(self, gac):
        gac.return_value = 10000000
        task = Classification()

        formquery = {
                     'id': 1234,
                     'start': '2013-01-01T00:00:00',
                     'end': '2013-10-10T00:00:00',
                     }

        with self.assertRaises(Invalid):
            task.formfields2taskargs(formquery, 'postgresql://localhost')
