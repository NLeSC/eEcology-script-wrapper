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
import colander
import script_wrapper.validation as swv


class TestValidateRange(unittest.TestCase):

    def test_inrange(self):
        self.assertTrue(swv.validateRange(5, 0, 10))

    def test_toolow(self):
        with self.assertRaises(swv.Invalid) as e:
            swv.validateRange(-5, 0, 10)

        self.assertEquals(e.exception.message,
                          'No data points selected for this script, please increase or shift time range')

    def test_toohigh(self):
        with self.assertRaises(swv.Invalid) as e:
            swv.validateRange(15, 0, 10)

        self.assertEquals(e.exception.message,
                          'Too many data points selected for this script, selected 15 data points while maximum is 10, please reduce time range and/or number of trackers')


class TestColorValidator(unittest.TestCase):
    def setUp(self):
        self.node = colander.SchemaNode(colander.String())

    def test_valid_uppercase(self):
        swv.colorValidator(self.node, '#11CC66')

    def test_valid_lowercase(self):
        swv.colorValidator(self.node, '#aabbcc')

    def test_namedcolor(self):
        with self.assertRaises(colander.Invalid) as cm:
            swv.colorValidator(self.node, 'blue')

        self.assertEqual(cm.exception.msg, '\'blue\' is not a color, should be #RRGGBB')

    def test_nonhex(self):
        with self.assertRaises(colander.Invalid) as cm:
            swv.colorValidator(self.node, '#ZZGGHH')

        self.assertEqual(cm.exception.msg, '\'#ZZGGHH\' is not a color, should be #RRGGBB')


class TestIso8601Validator(unittest.TestCase):
    def setUp(self):
        self.node = colander.SchemaNode(colander.String())

    def test_valid(self):
        swv.iso8601Validator(self.node, '2013-05-14T10:11:12Z')

    def test_invalid(self):
        with self.assertRaises(colander.Invalid) as cm:
            swv.iso8601Validator(self.node, 'May 14 2013 10:11:12')

        self.assertEqual(cm.exception.msg, 'Invalid date')
