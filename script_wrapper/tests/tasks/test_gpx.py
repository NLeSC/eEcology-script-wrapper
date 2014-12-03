from datetime import datetime
from unittest import TestCase
import pkgutil
from colander.iso8601 import UTC
from mock import patch, Mock
from script_wrapper.tasks.gpx import Gpx


class TestGpx(TestCase):
    def setUp(self):
        self.task = Gpx()

    @patch('script_wrapper.tasks.gpx.getGPSCount')
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

    def assertGpx(self, testname, doc):
        expected = pkgutil.get_data('script_wrapper.tests.data', testname + '.gpx')
        xml = doc.toGPX().toprettyxml('  ')
        self.assertMultiLineEqual(xml, expected)

    def test_track2gpx(self):
        task = self.task
        rows = [[datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC),  # dt
                 4.485608,  # lon
                 52.412252,   # lat
                 84,  # alt
                 ]]
        tracker_id = 1234

        result = task.track2gpx(tracker_id, rows)

        self.assertGpx('singlepoint', result)

    def test_getOutputFileName(self):
        task = self.task
        task.output_dir = Mock(return_value='/tmp/job1')
        tracker_id = 1234
        start = datetime(2013, 5, 14, 18, 01, 00, tzinfo=UTC)
        end = datetime(2013, 5, 15, 8, 33, 34, tzinfo=UTC)

        result = task.getOutputFileName(tracker_id, start, end)

        expected = '/tmp/job1/s201305141801-e201305150833-t1234.gpx'
        self.assertEqual(result, expected)
