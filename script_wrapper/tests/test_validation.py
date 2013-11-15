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
import script_wrapper.validation as swv


class TestValidateRange(unittest.TestCase):

    def testInRange(self):
        self.assertTrue(swv.validateRange(5, 0, 10))

    def testTooLow(self):
        with self.assertRaises(swv.Invalid) as e:
            swv.validateRange(-5, 0, 10)

        self.assertEquals(e.exception.message,
                          'No data points selected for this script, please increase or shift time range')

    def testTooHigh(self):
        with self.assertRaises(swv.Invalid) as e:
            swv.validateRange(15, 0, 10)

        self.assertEquals(e.exception.message,
                          'Too many data points selected for this script, please reduce time range and/or number of trackers')
