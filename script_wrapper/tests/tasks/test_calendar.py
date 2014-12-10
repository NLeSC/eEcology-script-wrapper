import unittest
from mock import Mock, patch
from script_wrapper.tasks.calendar import Calendar


class TestCalendar(unittest.TestCase):
    def setUp(self):
        self.task = Calendar()

    def test_run(self):
        task = self.task
        task.output_dir = Mock(return_value="/jobdir")
        task.update_state = Mock()
        task.r.calendar = Mock()

        db_url = 'postgresql://someone:somepass@somemachine/somedb'
        tracker_id = 1234
        start = '2013-05-14T10:11:12Z'
        end = '2013-05-15T08:33:34Z'
        result = task.run(db_url, tracker_id, start, end)

        expected = {'query': {'start': '2013-05-14T10:11:12Z',
                              'end': '2013-05-15T08:33:34Z',
                              'tracker_id': tracker_id,
                              }
                    }
        self.assertEqual(result, expected)
        task.r.calendar.called_with('someone',
                                    'somepass',
                                    'somedb',
                                    'somemachine',
                                    1234,
                                    '2013-05-14T10:11:12Z',
                                    '2013-05-15T08:33:34Z',
                                    )

    @patch('script_wrapper.tasks.calendar.getGPSCount')
    def test_formfields2taskargs(self, gpscount):
        gpscount.return_value = 400
        task = self.task

        fields = {'start': '2013-05-14T10:11:12Z',
                  'end': '2013-05-15T08:33:34Z',
                  'tracker_id': 1234,
                  }
        db_url = 'postgresql://someone:somepass@somemachine/somedb'

        result = task.formfields2taskargs(fields, db_url)

        expected = {'start': u'2013-05-14T10:11:12Z',
                    'end': u'2013-05-15T08:33:34Z',
                    'tracker_id': 1234,
                    'db_url': 'postgresql://someone:somepass@somemachine/somedb'
                    }
        self.assertEqual(result, expected)
        gpscount.assert_called_with('postgresql://someone:somepass@somemachine/somedb',
                                    1234,
                                    u'2013-05-14T10:11:12Z',
                                    u'2013-05-15T08:33:34Z',
                                    )
