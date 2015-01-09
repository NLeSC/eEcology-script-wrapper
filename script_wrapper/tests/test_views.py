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
from pyramid.exceptions import HTTPNotFound
from pyramid.response import FileResponse
from celery.result import AsyncResult
from script_wrapper.tasks import PythonTask
from script_wrapper.tasks.gpsvis_db import GpsVisDB as TaskMadeByResearcher
from script_wrapper.tasks.calendar import Calendar as TaskMadeByDeveloper
from script_wrapper.validation import Invalid
from script_wrapper.views import Views, TaskNotReady


class TestViews(unittest.TestCase):

    def setUp(self):
        self.settings = {'task_output_directory': '/tmp/results', }
        self.config = testing.setUp(settings=self.settings)
        self.request = testing.DummyRequest()

    def tearDown(self):
        testing.tearDown()

    def test_scriptid(self):
        self.request.matchdict = {'script': 'plot'}
        views = Views(self.request)

        self.assertEqual(views.scriptid, 'plot')

    def test_tasks_made_by_anyone(self):
        views = Views(self.request)
        taskMadeByResearcher = TaskMadeByResearcher()
        taskMadeByDeveloper = TaskMadeByDeveloper()
        views.celery.tasks = {
            'plot': taskMadeByResearcher,
            'kml': taskMadeByDeveloper,
            'celery.chain': 'celery.chain object',
        }

        tasks = views.tasks()

        expected_tasks = {
            'plot': taskMadeByResearcher,
            'kml': taskMadeByDeveloper,
        }
        self.assertEqual(tasks, expected_tasks)

    def test_tasks_made_by_researcher(self):
        views = Views(self.request)
        taskMadeByResearcher = TaskMadeByResearcher()
        taskMadeByDeveloper = TaskMadeByDeveloper()
        views.celery.tasks = {
            'plot': taskMadeByResearcher,
            'kml': taskMadeByDeveloper,
            'celery.chain': 'celery.chain object',
        }

        tasks = views.tasks(made_by_researcher=True)

        expected_tasks = {
            'plot': taskMadeByResearcher,
        }
        self.assertEqual(tasks, expected_tasks)

    def test_task(self):
        self.request.matchdict = {'script': 'plot'}
        views = Views(self.request)
        views.celery.tasks = {'plot': 'task1'}

        self.assertEqual(views.task(), 'task1')

    def test_task_invalidtaskname_notfound(self):
        self.request.matchdict = {'script': 'plotblablabla'}
        views = Views(self.request)

        with self.assertRaises(HTTPNotFound):
            views.task()

    def test_taskid(self):
        self.request.matchdict = {'taskid': 'b3c84d96-4dc7-4532-a864-3573202f202a'}
        views = Views(self.request)

        self.assertEqual(views.taskid, 'b3c84d96-4dc7-4532-a864-3573202f202a')

    def test_task_result(self):
        self.request.matchdict['taskid'] = 'b3c84d96-4dc7-4532-a864-3573202f202a'
        views = Views(self.request)
        mresult = Mock(AsyncResult)
        is_ready = True
        mresult.ready.return_value = is_ready
        views.celery.AsyncResult.return_value = mresult

        result = views.task_result()

        self.assertEqual(result, mresult)

    def test_task_result_must_be_ready(self):
        self.request.matchdict['taskid'] = 'b3c84d96-4dc7-4532-a864-3573202f202a'
        views = Views(self.request)
        mresult = Mock(AsyncResult)
        is_ready = True
        mresult.ready.return_value = is_ready
        views.celery.AsyncResult.return_value = mresult

        result = views.task_result(True)

        self.assertEqual(result, mresult)

    def test_task_result_must_be_ready_but_isnt(self):
        self.request.matchdict['taskid'] = 'b3c84d96-4dc7-4532-a864-3573202f202a'
        views = Views(self.request)
        mresult = Mock(AsyncResult)
        is_ready = False
        mresult.ready.return_value = is_ready
        views.celery.AsyncResult.return_value = mresult

        with self.assertRaises(TaskNotReady):
            views.task_result(True)

    def test_index(self):
        views = Views(self.request)
        taskMadeByResearcher = TaskMadeByResearcher()
        taskMadeByDeveloper = TaskMadeByDeveloper()
        views.celery.tasks = {
            'plot': taskMadeByResearcher,
            'kml': taskMadeByDeveloper,
            'celery.chain': 'celery.chain object',
        }

        result = views.index()

        expected_tasks = {
            'plot': taskMadeByResearcher,
        }
        self.assertEqual(result, {'tasks': expected_tasks})

    def test_form(self):
        self.request.matchdict['script'] = 'plot'
        views = Views(self.request)
        views.celery.tasks = {'plot': 'task1'}

        result = views.form()

        self.assertEqual(result, {'task': 'task1'})

    def test_jsform(self):
        from tempfile import NamedTemporaryFile
        formjs = NamedTemporaryFile(suffix='.js')
        task = PythonTask()
        task.js_form_location = Mock(return_value=formjs.name)
        self.request.matchdict['script'] = 'plot'
        views = Views(self.request)
        views.celery.tasks = {'plot': task}

        result = views.jsform()

        self.assertIsInstance(result, FileResponse)
        self.assertEqual(result.content_type, 'application/javascript')
        formjs.close()

    @patch('script_wrapper.views.db_url_from_request')
    def test_submit(self, dr):
        dr.return_value = 'sqlite:///'
        self.config.add_route('result', '/{taskid}')
        self.request.matchdict['script'] = 'plot'
        self.request.json_body = 1234
        task = Mock(PythonTask)
        task_result = Mock(AsyncResult)
        task_result.id = 'b3c84d96-4dc7-4532-a864-3573202f202a'
        task.apply_async.return_value = task_result
        views = Views(self.request)
        views.celery.tasks = {'plot': task}

        result = views.submit()

        eresult = {'success': True,
                   'result': '/b3c84d96-4dc7-4532-a864-3573202f202a',
                   }
        self.assertEqual(result, eresult)
        task.formfields2taskargs.assert_called_with(1234, 'sqlite:///')

    @patch('script_wrapper.views.db_url_from_request')
    def test_submit_InvalidQuery(self, dr):
        dr.return_value = 'sqlite:///'
        self.request.matchdict['script'] = 'plot'
        self.request.json_body = 1234
        task = Mock(PythonTask)
        task.formfields2taskargs.side_effect = Invalid('Invalid query')
        views = Views(self.request)
        views.celery.tasks = {'plot': task}

        result = views.submit()

        eresult = {'success': False,
                   'msg': 'Invalid query'}
        self.assertEqual(result, eresult)

    @patch('script_wrapper.views.db_url_from_request')
    def test_submit_InvalidQueryField(self, dr):
        dr.return_value = 'sqlite:///'
        self.request.matchdict['script'] = 'kmzgen'
        self.request.json_body = {'shape': 'triangle'}
        task = Mock(PythonTask)

        import colander

        shape = colander.SchemaNode(colander.String(),
                                    name='shape',
                                    validator=colander.OneOf(['circle', 'iarrow', 'tarrow']))
        exception = colander.Invalid(shape, '"triangle" is not one of circle, iarrow, tarrow')
        task.formfields2taskargs.side_effect = exception
        views = Views(self.request)
        views.celery.tasks = {'kmzgen': task}

        result = views.submit()

        eresult = {'success': False,
                   'errors': {'shape': '"triangle" is not one of circle, iarrow, tarrow'},
                   }
        self.assertEqual(result, eresult)

    def test_statejson(self):
        self.config.add_route('result', '/{script}/{taskid}')
        self.request.matchdict['script'] = 'plot'
        self.request.matchdict['taskid'] = 'b3c84d96-4dc7-4532-a864-3573202f202a'
        views = Views(self.request)
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

    def test_statehtml(self):
        result_url = '/plot/b3c84d96-4dc7-4532-a864-3573202f202a'
        state = {'state': 'PENDING',
                 'success': False,
                 'failure': False,
                 'ready': False,
                 'result': result_url,
                 'task': 'pythontask',
                 }
        self.request.matchdict['script'] = 'plot'
        views = Views(self.request)
        views.statejson = Mock(return_value=state)
        views.celery.tasks = {'plot': 'pythontask'}

        result = views.statehtml()

        self.assertDictEqual(result, state)

    @patch('os.listdir')
    def test_result(self, listdir):
        self.config.add_route('result_file', '/{script}/{taskid}/{filename}')
        self.request.matchdict['script'] = 'plot'
        self.request.matchdict['taskid'] = 'mytaskid'
        views = Views(self.request)
        task_result = Mock(AsyncResult)
        task_result.id = 'mytaskid'
        task_result.ready.return_value = True
        task_result.failed.return_value = False
        views.celery.AsyncResult = Mock(return_value=task_result)
        task = PythonTask()
        task.name = 'plot'
        views.celery.tasks = {'plot': task}
        listdir.return_value = ['stderr.txt', 'stdout.txt']

        result = views.result()

        eresult = {'result': task_result,
                   'files': {'stderr.txt': '/plot/mytaskid/stderr.txt',
                             'stdout.txt': '/plot/mytaskid/stdout.txt',
                             },
                   'task': task,
                   'result_html': None,
                   }
        self.assertEqual(result, eresult)
        listdir.assert_called_with('/tmp/results/mytaskid')

    @patch('os.listdir')
    def test_result_nofiles(self, listdir):
        self.request.matchdict['script'] = 'plot'
        self.request.matchdict['taskid'] = 'mytaskid'
        views = Views(self.request)
        task_result = Mock(AsyncResult)
        task_result.ready.return_value = True
        task_result.failed.return_value = False
        views.celery.AsyncResult = Mock(return_value=task_result)
        task = PythonTask()
        task.name = 'plot'
        views.celery.tasks = {'plot': task}
        listdir.side_effect = OSError('[Errno 2] No such file or directory: /tmp/results/mytaskid')

        result = views.result()

        eresult = {'result': task_result,
                   'files': {},
                   'task': task,
                   'result_html': None,
                   }
        self.assertEqual(result, eresult)

    def test_result_template(self):
        self.request.matchdict['script'] = 'plot'
        self.request.matchdict['taskid'] = 'mytaskid'
        views = Views(self.request)
        task_result = Mock(AsyncResult)
        views.task_result = Mock(return_value=task_result)
        task = PythonTask()
        task.render_result = Mock(return_value='mytemplate')
        views.task = Mock(return_value=task)
        files = {'result.csv': '/plot/mytaskid/result.csv', }
        views.result_files = Mock(return_value=files)

        result = views.result()

        eresult = {'result': task_result,
                   'files': files,
                   'task': task,
                   'result_html': 'mytemplate',
                   }
        self.assertEqual(result, eresult)

    @patch('script_wrapper.views.FileResponse')
    def test_result_file(self, fileresponse):
        self.request.matchdict['script'] = 'plot'
        self.request.matchdict['taskid'] = 'mytaskid'
        self.request.matchdict['filename'] = 'stdout.txt'
        views = Views(self.request)
        task_result = Mock(AsyncResult)
        task_result.id = 'mytaskid'
        task_result.ready.return_value = True
        views.celery.AsyncResult = Mock(return_value=task_result)

        views.result_file()

        epath = '/tmp/results/mytaskid/stdout.txt'
        fileresponse.assert_called_with(epath, self.request)

    @patch('script_wrapper.views.make_session_from_request')
    def test_species(self, sm):
        session = Mock()
        mock_species = ['Lesser Black-backed Gull']
        config = {'return_value.query.return_value.distinct.return_value.order_by.return_value': mock_species}
        session.configure_mock(**config)
        sm.return_value = session
        views = Views(self.request)

        species = views.species()

        self.assertEqual(species, [{'id': 'Lesser Black-backed Gull',
                                    'text': 'Lesser Black-backed Gull',
                                    }])

    @patch('script_wrapper.views.make_session_from_request')
    def test_projects(self, sm):
        session = Mock()
        mock_projects = [('Project1')]
        config = {'return_value.query.return_value.distinct.return_value.order_by.return_value': mock_projects}
        session.configure_mock(**config)
        sm.return_value = session
        views = Views(self.request)

        projects = views.projects()

        self.assertEqual(projects, [{'id': 'Project1',
                                     'text': 'Project1',
                                     }])

    @patch('script_wrapper.views.make_session_from_request')
    def test_trackers(self, sm):
        session = Mock()
        mock_trackers = [(1, 'Project1', 'Lesser Black-backed Gull')]
        config = {'return_value.query.return_value.join.return_value.join.return_value.order_by.return_value.distinct.return_value': mock_trackers}
        session.configure_mock(**config)
        sm.return_value = session
        views = Views(self.request)

        trackers = views.trackers()

        self.assertEqual(trackers, [{'id': 1,
                                     'project': 'Project1',
                                     'species': 'Lesser Black-backed Gull',
                                     }])

    def test_revoke_task(self):
        self.request.matchdict['taskid'] = 'mytaskid'
        views = Views(self.request)
        task_result = Mock(AsyncResult)
        task_result.failed.return_value = False
        views.celery = Mock()
        views.celery.AsyncResult = Mock(return_value=task_result)

        result = views.revoke_task()

        self.assertEquals(result, {'success': True})
        views.celery.AsyncResult.assert_called_with('mytaskid')
        task_result.revoke.assert_called_with(terminate=True)

    def test_tools(self):
        self.config.add_route('apply', '/tool/{script}/')
        views = Views(self.request)
        taskMadeByResearcher = TaskMadeByResearcher()
        taskMadeByDeveloper = TaskMadeByDeveloper()
        views.celery.tasks = {
            'plot': taskMadeByResearcher,
            'kml': taskMadeByDeveloper,
            'celery.chain': 'celery.chain object',
        }

        result = views.tools()

        expected = [{
            'label': 'Calendar',
            'form_url': '/tool/calendar/',
            'title': 'Calendar overview with daily statistics of GPS-tracker',
            'description': '''More information can be found <a target="_blank" href="https://services.e-ecology.sara.nl/wiki/index.php/Calendar">here</a>.''',
            'made_by_researcher': False
        }, {
            'label': 'KMZ and Plot',
            'form_url': '/tool/gpsvis_db/',
            'title': 'Generate KMZ file and statistics plot',
            'description': '',
            'made_by_researcher': True
        }]
        self.assertEquals(result, expected)
