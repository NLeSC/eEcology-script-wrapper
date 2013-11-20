from datetime import datetime
import unittest
from mock import patch
from pytz import UTC
from script_wrapper.tasks.pykml import PyKML

class Test(unittest.TestCase):
    def test_create_styles(self):
        task = PyKML()
        styles = task.create_styles()

        self.assertEqual(len(styles), 15)

    def test_speed2style_validspeeds(self):
        task = PyKML()
        base_color = 'FF7711'
        styles = {
                  'FF7711': [
                             'style1',
                             'style2',
                             'style3',
                             'style4',
                             ]
                  }

        speeds = {
                  50: 'style1',
                  15: 'style2',
                  7: 'style3',
                  3: 'style4',
                  }
        for spd, style in speeds.iteritems():
            result = task.speed2style(styles, base_color, spd)
            self.assertEqual(result, style)

    def test_speed2style_invalidbasecolor(self):
        task = PyKML()
        with self.assertRaises(KeyError):
            task.speed2style({}, 'FF7711', 13)

    @patch('script_wrapper.tasks.pykml.getGPSCount')
    def test_formfields2taskargs_noerrors(self, gpscount):
        gpscount.return_value = 400
        task = PyKML()
        formfields = {
                      'start': '2013-05-14T10:11:12Z',
                      'end': '2013-05-15T08:33:34Z',
                      'trackers': [{'id': 1234, 'color': '1177FF'}]
                      }
        db_url = 'postgresql://localhost/eecology'
        taskargs = task.formfields2taskargs(formfields, db_url)

        etaskargs = {'db_url': 'postgresql://localhost/eecology',
                     'end': datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),
                     'start': datetime(2013, 5, 14, 10, 11, 12, tzinfo=UTC),
                     'trackers': [{'color': '1177FF', 'id': 1234}]
                     }
        self.assertDictEqual(taskargs, etaskargs)
