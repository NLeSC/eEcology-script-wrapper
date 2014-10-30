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
from mock import Mock, patch
from pyramid.testing import DummyRequest
from pytz import UTC
from sqlalchemy.orm import Session, Query
from script_wrapper import models


class TestModels(unittest.TestCase):

    def test_GPS_SCHEMA(self):
        self.assertEqual('gps', models.GPS_SCHEMA)

    def test_request_credentials(self):
        req = DummyRequest()
        req.environ['HTTP_AUTHORIZATION'] = 'Basic bWU6cGFzc3dvcmQ=\n'

        creds = models.request_credentials(req)

        self.assertEqual(creds, ('me', 'password'))

    def test_request_credentials_nonbasic(self):
        req = DummyRequest()
        req.environ['HTTP_AUTHORIZATION'] = 'MAC bWU6cGFzc3dvcmQ=\n'

        with self.assertRaises(NotImplementedError):
            models.request_credentials(req)

    def test_request_credentials_noauth(self):
        req = DummyRequest()

        creds = models.request_credentials(req)

        self.assertEqual(creds, (None, None))

    def test_db_url_from_request(self):
        req = DummyRequest()
        odb_url = 'postgresql://localhost?ssl=true'
        req.registry.settings = {}
        req.registry.settings['sqlalchemy.url'] = odb_url
        req.environ['HTTP_AUTHORIZATION'] = 'Basic bWU6cGFzc3dvcmQ=\n'

        db_url = models.db_url_from_request(req)

        edb_url = 'postgresql://me:password@localhost?ssl=true'
        self.assertEqual(db_url, edb_url)

    @patch('script_wrapper.models.DBSession')
    def test_getAccelerationCount(self, dbsession):
        db_url = 'postgresql://localhost?ssl=true'
        device_info_serial = 1234
        start = datetime(2013, 1, 1, tzinfo=UTC)
        end = datetime(2013, 12, 12, tzinfo=UTC)
        query = Mock(Query)
        session = Mock(Session)
        session.query.return_value = query
        dbsession.return_value = session

        models.getAccelerationCount(db_url, device_info_serial, start, end)

        query.count.assert_called()


class TestSpeed(unittest.TestCase):
    def test_speedtrajectdirection_sql(self):
        result = models.Speed.trajectDirection
        expectedsql = 'round(CAST(degrees(ST_Azimuth(lag(gps.ee_tracking_speed_limited.location) OVER (ORDER BY gps.ee_tracking_speed_limited.device_info_serial, gps.ee_tracking_speed_limited.date_time), gps.ee_tracking_speed_limited.location)) AS NUMERIC), :round_1)'
        self.assertEqual(str(result), expectedsql)
        self.assertEqual(result.name, 'tdirection')
        expectedparams = {'round_1': 2}
        self.assertEqual(result.compile().params, expectedparams)

    def test_speedtrajectspeed_sql(self):
        result = models.Speed.trajectSpeed
        expectedsql = 'round(CAST(ST_Length_Spheroid(ST_MakeLine(gps.ee_tracking_speed_limited.location, lag(gps.ee_tracking_speed_limited.location) OVER (ORDER BY gps.ee_tracking_speed_limited.device_info_serial, gps.ee_tracking_speed_limited.date_time)), :ST_Length_Spheroid_1) / EXTRACT(epoch FROM gps.ee_tracking_speed_limited.date_time - lag(gps.ee_tracking_speed_limited.date_time) OVER (ORDER BY gps.ee_tracking_speed_limited.device_info_serial, gps.ee_tracking_speed_limited.date_time)) AS NUMERIC), :round_1)'
        self.assertEqual(str(result), expectedsql)
        # TODO compare bind/params
        self.assertEqual(result.name, 'tspeed')

    def test_elevation_sql(self):
        self.maxDiff = None
        result = models.Speed.elevation
        expectedsql = """coalesce(nullif(
                (
                SELECT max(the_data[floor(((st_ymax(bbox) - (st_y(location))) / abs(cellsize_y))+1)]
                         [floor(((st_x(location)- st_xmin(bbox)) / abs(cellsize_x))+1)])::float
                FROM elevation.srtm3
                WHERE bbox && location
                )
            , -9999
            )
            , (
            SELECT max(the_data[floor(((st_ymax(bbox) - (st_y(location))) / abs(cellsize_y))+1)]
                     [floor(((st_x(location)- st_xmin(bbox)) / abs(cellsize_x))+1)])::float
            FROM elevation.srtm30
            WHERE bbox && location
            )
        )
        """
        self.assertMultiLineEqual(str(result), expectedsql)
        self.assertEqual(result.name, 'elevation')
