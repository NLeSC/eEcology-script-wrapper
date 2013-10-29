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
from pyramid.httpexceptions import HTTPFound
from celery.result import AsyncResult
from script_wrapper.tasks import PythonTask
from script_wrapper.validation import Invalid
from script_wrapper.views import Views


class TestViews(unittest.TestCase):

    def setUp(self):
        self.settings = {}
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
        self.config.add_route('state', '/{taskid}/state')
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
                   'state': '/b3c84d96-4dc7-4532-a864-3573202f202a/state',
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
        self.config.add_route('result', '/{script}/{taskid}/result')
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

        result_url = '/plot/b3c84d96-4dc7-4532-a864-3573202f202a/result'
        expected_result = {'state': 'PENDING',
                           'ready': False,
                           'success': False,
                           'failure': False,
                           'result': result_url}
        self.assertDictEqual(result, expected_result)

    def testStateHtmlPending(self):
        result_url = '/plot/b3c84d96-4dc7-4532-a864-3573202f202a/result'
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

    def testStateHtmlFinished(self):
        result_url = '/plot/b3c84d96-4dc7-4532-a864-3573202f202a/result'
        state = {'state': 'STOPPED',
                 'success': True,
                 'ready': True,
                 'failure': False,
                 'result': result_url,
                 'task': 'pythontask',
                 }
        request = testing.DummyRequest()
        request.matchdict['script'] = 'plot'
        views = Views(request)
        views.statejson = Mock(return_value=state)
        views.celery.tasks = {'plot': 'pythontask'}

        result = views.statehtml()

        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, result_url)

    def testResultMultipleFiles(self):
        self.config.add_route('result_file',
                              '/{script}/{taskid}/result/{filename}')
        request = testing.DummyRequest()
        request.matchdict['script'] = 'plot'
        request.matchdict['taskid'] = 'mytaskid'
        views = Views(request)
        task_result = Mock(AsyncResult)
        task_result.id = 'mytaskid'
        task_result.failed.return_value = False
        task_result.result = {'files': {'stdout.txt': '/tmp/stdout.txt',
                                        'stderr.txt': '/tmp/stderr.txt',
                                        }
                              }
        views.celery.AsyncResult = Mock(return_value=task_result)
        views.celery.tasks = {'plot': 'pythontask'}

        result = views.result()

        efiles = {'stderr.txt': '/plot/mytaskid/result/stderr.txt',
                  'stdout.txt': '/plot/mytaskid/result/stdout.txt',
                  }
        self.assertDictEqual(result, {'files': efiles,
                                      'task': 'pythontask',
                                      })

    def testResultSingleFiles(self):
        self.config.add_route('result_file', '/{script}/{taskid}/result/{filename}')
        request = testing.DummyRequest()
        request.matchdict['script'] = 'plot'
        request.matchdict['taskid'] = 'mytaskid'
        views = Views(request)
        task_result = Mock(AsyncResult)
        task_result.id = 'mytaskid'
        task_result.failed.return_value = False
        task_result.result = {'files': {
                                        'stdout.txt': '/tmp/stdout.txt',
                                        }
                              }
        views.celery.AsyncResult = Mock(return_value=task_result)

        result = views.result()

        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, '/plot/mytaskid/result/stdout.txt')

    def testResultFailure(self):
        request = testing.DummyRequest()
        request.matchdict['script'] = 'plot'
        request.matchdict['taskid'] = 'mytaskid'
        views = Views(request)
        task_result = Mock(AsyncResult)
        task_result.id = 'mytaskid'
        task_result.failed.return_value = True

        class TaskException(Exception):
            pass

        task_result.result = TaskException()
        views.celery.AsyncResult = Mock(return_value=task_result)

        with self.assertRaises(TaskException):
            views.result()

    def testResultFile(self):
        from tempfile import NamedTemporaryFile
        out = NamedTemporaryFile(suffix='.txt')

        request = testing.DummyRequest()
        request.matchdict['script'] = 'plot'
        request.matchdict['taskid'] = 'mytaskid'
        request.matchdict['filename'] = 'stdout.txt'
        views = Views(request)
        task_result = Mock(AsyncResult)
        task_result.id = 'mytaskid'
        task_result.failed.return_value = False
        task_result.result = {'files': {'stdout.txt': out.name,
                                        }
                              }
        views.celery.AsyncResult = Mock(return_value=task_result)

        result = views.result_file()

        self.assertIsInstance(result, FileResponse)
        self.assertEqual(result.content_type, 'text/plain')

        out.close()

    def testResultFileFailure(self):
        request = testing.DummyRequest()
        request.matchdict['script'] = 'plot'
        request.matchdict['taskid'] = 'mytaskid'
        views = Views(request)
        task_result = Mock(AsyncResult)
        task_result.id = 'mytaskid'
        task_result.failed.return_value = True

        class TaskException(Exception):
            pass

        task_result.result = TaskException()
        views.celery.AsyncResult = Mock(return_value=task_result)

        with self.assertRaises(TaskException):
            views.result_file()

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
