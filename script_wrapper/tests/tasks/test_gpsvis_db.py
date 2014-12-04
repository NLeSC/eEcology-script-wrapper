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
from pytz import UTC
from script_wrapper.tasks.gpsvis_db import GpsVisDB


class TestClassification(unittest.TestCase):

    def test_matlab_version(self):
        task = GpsVisDB()
        self.assertEqual(task.matlab_version, '2012b')

    def test_convert_colors_valids(self):
        task = GpsVisDB()

        colors = {'FFFF50': 1,
                  'F7E8AA': 2,
                  'FFA550': 3,
                  '5A5AFF': 4,
                  'BEFFFF': 5,
                  '8CFF8C': 6,
                  'FF8CFF': 7,
                  'AADD96': 8,
                  'FFD3AA': 9,
                  'C6C699': 10,
                  'E5BFC6': 11,
                  'DADADA': 12,
                  'C6B5C4': 13,
                  'C1D1BF': 14,
                  '000000': 15
                  }
        for (code, index) in colors.iteritems():
            result = task.convert_colors({'id': 1, 'color': code,
                                          'size': 'small', 'speed': 1})
            self.assertEquals(result, index)

    def test_convert_colors_notfound(self):
        task = GpsVisDB()

        with self.assertRaises(ValueError):
            task.convert_colors({'id': 1, 'color': 'blue',
                                 'size': 'small', 'speed': 1})

    @patch('script_wrapper.tasks.gpsvis_db.getGPSCount')
    def test_formfields2taskargs(self, gps_count):
        gps_count.return_value = 1000
        task = GpsVisDB()

        trackers = [{'id': 1, 'color': 'DADADA',
                     'size': 'small', 'speed': 1}]
        formquery = {'trackers': trackers,
                     'start': '2013-01-01T00:00:00',
                     'end': '2013-10-10T00:00:00',
                     'alt': 'clampToGround',
                     }

        taskargs = task.formfields2taskargs(formquery,
                                            'postgresql://localhost')

        etrackers = [{'id': 1, 'color': 12,
                      'size': 'small', 'speed': 1}]
        etaskargs = {'db_url': 'postgresql://localhost',
                     'start': '2013-01-01T00:00:00',
                     'end': '2013-10-10T00:00:00',
                     'alt': 'clampToGround',
                     'trackers': etrackers,
                     }

        self.assertEqual(taskargs, etaskargs)
