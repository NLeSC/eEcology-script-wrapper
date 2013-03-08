import unittest
from pyramid.testing import DummyRequest
from sqlalchemy.orm import Session
from trackertask import models

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



