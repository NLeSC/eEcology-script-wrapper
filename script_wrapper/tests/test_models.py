from datetime import datetime
import unittest
from mock import Mock, patch
from pyramid.testing import DummyRequest
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
        start = datetime(2013, 1, 1)
        end = datetime(2013, 12, 12)
        query = Mock(Query)
        session = Mock(Session)
        session.query.return_value = query
        dbsession.return_value = session

        models.getAccelerationCount(db_url, device_info_serial, start, end)

        query.count.assert_called()


