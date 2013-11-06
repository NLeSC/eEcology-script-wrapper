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
from mock import Mock, patch
from pyramid import testing
from pyramid.response import FileResponse
from celery.result import AsyncResult
from script_wrapper.tasks import PythonTask
from script_wrapper.validation import Invalid
from script_wrapper.views import Views, TaskNotReady


class TestViews(unittest.TestCase):

    def setUp(self):
        self.settings = {
                         'task_output_directory': '/tmp/results',
                         }
        self.config = testing.setUp(settings=self.settings)

    def tearDown(self):
        testing.tearDown()

    def testScriptId(self):
        request = testing.DummyRequest()
        request.matchdict = {'script': 'plot'}
        views = Views(request)

        self.assertEqual(views.scriptid, 'plot')

    def testTaskId(self):
        request = testing.DummyRequest()
        request.matchdict = {'taskid': 'b3c84d96-4dc7-4532-a864-3573202f202a'}
        views = Views(request)

        self.assertEqual(views.taskid, 'b3c84d96-4dc7-4532-a864-3573202f202a')

    def test_task_result(self):
        request = testing.DummyRequest()
        request.matchdict['taskid'] = 'b3c84d96-4dc7-4532-a864-3573202f202a'
        views = Views(request)
        mresult = Mock(AsyncResult)
        is_ready = True
        mresult.ready.return_value = is_ready
        views.celery.AsyncResult.return_value = mresult

        result = views.task_result()

        self.assertEqual(result, mresult)

    def test_task_result_must_be_ready(self):
        request = testing.DummyRequest()
        request.matchdict['taskid'] = 'b3c84d96-4dc7-4532-a864-3573202f202a'
        views = Views(request)
        mresult = Mock(AsyncResult)
        is_ready = True
        mresult.ready.return_value = is_ready
        views.celery.AsyncResult.return_value = mresult

        result = views.task_result(True)

        self.assertEqual(result, mresult)

    def test_task_result_must_be_ready_but_isnt(self):
        request = testing.DummyRequest()
        request.matchdict['taskid'] = 'b3c84d96-4dc7-4532-a864-3573202f202a'
        views = Views(request)
        mresult = Mock(AsyncResult)
        is_ready = False
        mresult.ready.return_value = is_ready
        views.celery.AsyncResult.return_value = mresult

        with self.assertRaises(TaskNotReady):
            views.task_result(True)

    def testIndex(self):
        request = testing.DummyRequest()
        views = Views(request)
        views.celery.tasks = {'plot': 'task1'}

        result = views.index()

        self.assertEqual(result, {'tasks': {'plot': 'task1'}})

    def testForm(self):
        request = testing.DummyRequest()
        request.matchdict['script'] = 'plot'
        views = Views(request)
        views.celery.tasks = {'plot': 'task1'}

        result = views.form()

        self.assertEqual(result, {'task': 'task1'})

    def testJsForm(self):
        from tempfile import NamedTemporaryFile
        formjs = NamedTemporaryFile(suffix='.js')
        task = PythonTask()
        task.js_form_location = Mock(return_value=formjs.name)
        request = testing.DummyRequest()
        request.matchdict['script'] = 'plot'
        views = Views(request)
        views.celery.tasks = {'plot': task}

        result = views.jsform()

        self.assertIsInstance(result, FileResponse)
        self.assertEqual(result.content_type, 'application/javascript')
        formjs.close()

    @patch('script_wrapper.views.db_url_from_request')
    def testSubmit(self, dr):
        dr.return_value = 'sqlite:///'
        self.config.add_route('result', '/{taskid}')
        request = testing.DummyRequest()
        request.matchdict['script'] = 'plot'
        request.json_body = 1234
        task = Mock(PythonTask)
        task_result = Mock(AsyncResult)
        task_result.id = 'b3c84d96-4dc7-4532-a864-3573202f202a'
        task.apply_async.return_value = task_result
        views = Views(request)
        views.celery.tasks = {'plot': task}

        result = views.submit()

        eresult = {'success': True,
                   'result': '/b3c84d96-4dc7-4532-a864-3573202f202a',
                   }
        self.assertEqual(result, eresult)
        task.formfields2taskargs.assert_called_with(1234, 'sqlite:///')

    @patch('script_wrapper.views.db_url_from_request')
    def testSubmit_InvalidQuery(self, dr):
        dr.return_value = 'sqlite:///'
        request = testing.DummyRequest()
        request.matchdict['script'] = 'plot'
        request.json_body = 1234
        task = Mock(PythonTask)
        task.formfields2taskargs.side_effect = Invalid('Invalid query')
        views = Views(request)
        views.celery.tasks = {'plot': task}

        result = views.submit()

        eresult = {'success': False,
                   'msg': 'Invalid query'}
        self.assertEqual(result, eresult)

    def testStateJson(self):
        self.config.add_route('result', '/{script}/{taskid}')
        request = testing.DummyRequest()
        request.matchdict['script'] = 'plot'
        request.matchdict['taskid'] = 'b3c84d96-4dc7-4532-a864-3573202f202a'
        views = Views(request)
        task_result = Mock(AsyncResult)
        task_result.id = 'b3c84d96-4dc7-4532-a864-3573202f202a'
        task_result.state = 'PENDING'
        task_result.ready.return_value = False
        task_result.successful.return_value = False
        task_result.failed.return_value = False
        views.celery.AsyncResult = Mock(return_value=task_result)

        result = views.statejson()

        result_url = '/plot/b3c84d96-4dc7-4532-a864-3573202f202a'
        expected_result = {'state': 'PENDING',
                           'ready': False,
                           'success': False,
                           'failure': False,
                           'result': result_url}
        self.assertDictEqual(result, expected_result)

    def testStateHtml(self):
        result_url = '/plot/b3c84d96-4dc7-4532-a864-3573202f202a'
        state = {'state': 'PENDING',
                 'success': False,
                 'failure': False,
                 'ready': False,
                 'result': result_url,
                 'task': 'pythontask',
                 }
        request = testing.DummyRequest()
        request.matchdict['script'] = 'plot'
        views = Views(request)
        views.statejson = Mock(return_value=state)
        views.celery.tasks = {'plot': 'pythontask'}

        result = views.statehtml()

        self.assertDictEqual(result, state)

    @patch('os.listdir')
    def testResult(self, listdir):
        request = testing.DummyRequest()
        request.matchdict['script'] = 'plot'
        request.matchdict['taskid'] = 'mytaskid'
        views = Views(request)
        task_result = Mock(AsyncResult)
        task_result.id = 'mytaskid'
        task_result.ready.return_value = True
        task_result.failed.return_value = False
        views.celery.AsyncResult = Mock(return_value=task_result)
        views.celery.tasks = {'plot': 'pythontask'}
        listdir.return_value = ['stderr.txt', 'stdout.txt']

        result = views.result()

        eresult = {
                   'result': task_result,
                   'files': ['stderr.txt', 'stdout.txt'],
                   'task': 'pythontask',
                   }
        self.assertEqual(result, eresult)
        listdir.assert_called_with('/tmp/results/mytaskid')

    @patch('os.listdir')
    def test_result_nofiles(self, listdir):
        request = testing.DummyRequest()
        request.matchdict['script'] = 'plot'
        request.matchdict['taskid'] = 'mytaskid'
        views = Views(request)
        task_result = Mock(AsyncResult)
        task_result.id = 'mytaskid'
        task_result.ready.return_value = True
        task_result.failed.return_value = False
        views.celery.AsyncResult = Mock(return_value=task_result)
        views.celery.tasks = {'plot': 'pythontask'}
        listdir.side_effect = OSError('[Errno 2] No such file or directory: /tmp/results/mytaskid')

        result = views.result()

        eresult = {
                   'result': task_result,
                   'files': [],
                   'task': 'pythontask',
                   }
        self.assertEqual(result, eresult)

    @patch('script_wrapper.views.FileResponse')
    def testResultFile(self, fileresponse):
        request = testing.DummyRequest()
        request.matchdict['script'] = 'plot'
        request.matchdict['taskid'] = 'mytaskid'
        request.matchdict['filename'] = 'stdout.txt'
        views = Views(request)
        task_result = Mock(AsyncResult)
        task_result.id = 'mytaskid'
        task_result.ready.return_value = True
        views.celery.AsyncResult = Mock(return_value=task_result)

        views.result_file()

        epath = '/tmp/results/mytaskid/stdout.txt'
        fileresponse.assert_called_with(epath, request)

    @patch('script_wrapper.views.make_session_from_request')
    def testSpecies(self, sm):
        session = Mock()
        mock_species = ['Lesser Black-backed Gull']
        config = {'return_value.query.return_value.distinct.return_value.order_by.return_value': mock_species}
        session.configure_mock(**config)
        sm.return_value = session
        request = testing.DummyRequest()
        views = Views(request)

        species = views.species()

        self.assertEqual(species, [{'id': 'Lesser Black-backed Gull',
                                    'text': 'Lesser Black-backed Gull',
                                    }])

    @patch('script_wrapper.views.make_session_from_request')
    def testProjects(self, sm):
        session = Mock()
        mock_projects = [('Project1')]
        config = {'return_value.query.return_value.distinct.return_value.order_by.return_value': mock_projects}
        session.configure_mock(**config)
        sm.return_value = session
        request = testing.DummyRequest()
        views = Views(request)

        projects = views.projects()

        self.assertEqual(projects, [{'id': 'Project1',
                                    'text': 'Project1',
                                    }])

    @patch('script_wrapper.views.make_session_from_request')
    def testTrackers(self, sm):
        session = Mock()
        mock_trackers = [(1, 'Project1', 'Lesser Black-backed Gull')]
        config = {'return_value.query.return_value.join.return_value.join.return_value.order_by.return_value.distinct.return_value': mock_trackers}
        session.configure_mock(**config)
        sm.return_value = session
        request = testing.DummyRequest()
        views = Views(request)

        trackers = views.trackers()

        self.assertEqual(trackers, [{'id': 1,
                                    'project': 'Project1',
                                    'species': 'Lesser Black-backed Gull',
                                    }])


    def test_revoke_task(self):
        request = testing.DummyRequest()
        request.matchdict['taskid'] = 'mytaskid'
        views = Views(request)
        task_result = Mock(AsyncResult)
        task_result.failed.return_value = False
        views.celery = Mock()
        views.celery.AsyncResult = Mock(return_value=task_result)

        result = views.revoke_task()

        self.assertEquals(result, {'success': True})
        views.celery.AsyncResult.assert_called_with('mytaskid')
        task_result.revoke.assert_called_with(terminate=True)
