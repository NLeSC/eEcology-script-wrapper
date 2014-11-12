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

import os
import logging
from celery import current_app as celery
from pyramid.exceptions import HTTPNotFound
from pyramid.response import FileResponse
from pyramid.view import view_config
from script_wrapper.models import make_session_from_request
from script_wrapper.models import db_url_from_request
from script_wrapper.models import Tracker, Individual, TrackSession
from script_wrapper.validation import Invalid

logger = logging.getLogger(__package__)


class TaskNotReady(Exception):
    pass


class Views(object):
    """Container for all views of script wrapper web application"""
    def __init__(self, request):
        self.request = request
        self.celery = celery

    @property
    def scriptid(self):
        """Script identifier or task name, derived from url"""
        return self.request.matchdict['script']

    @property
    def taskid(self):
        """Task identifier, derived from url"""
        return self.request.matchdict['taskid']

    def tasks(self, made_by_researcher=None):
        """Return dict of available tasks.

        Key is task name and value is task object

        Parameters:
        made_by_researcher: boolean
            if true then only returns tasks made by researchers
        """
        items = self.celery.tasks.iteritems()
        tasks = {k: v for k, v in items if not k.startswith('celery.')}
        if made_by_researcher:
            # only return tasks which have been made by researchers
            tasks = {k: v for k, v in tasks.iteritems() if v.made_by_researcher}
        return tasks

    def task(self):
        """Returns current task object"""
        try:
            return self.tasks()[self.scriptid]
        except KeyError:
            raise HTTPNotFound

    def task_result(self, must_be_ready=False):
        """Fetches result for `self.taskid`.

        If task failed raises it's exception.

        ``must_be_ready`` If true raises TaskNotReady when result is not ready.
        """
        result = self.celery.AsyncResult(self.taskid)
        # An unknown taskid will return a PENDING state
        # TODO distinguish between pending job and unknown job.

        if must_be_ready and not result.ready():
            raise TaskNotReady()

        return result

    def task_result_directory(self):
        """Returns result director of current task"""
        base = self.request.registry.settings['task_output_directory']
        directory = os.path.join(base, self.taskid)
        return directory

    @view_config(route_name='index', renderer='index.mak')
    def index(self):
        """Show list of scripts made by researchers"""
        return {'tasks': self.tasks(made_by_researcher=True)}

    @view_config(route_name='apply', request_method='GET', renderer='form.mak')
    def form(self):
        """Returns html form of selected task"""
        return {'task': self.task()}

    @view_config(route_name='jsform')
    def jsform(self):
        """Returns javascript form of selected task"""
        task = self.task()
        return FileResponse(task.js_form_location(), self.request)

    @view_config(route_name='apply', request_method='POST', renderer='json')
    def submit(self):
        """Process task submission

        The submission will be validated and submitted to the task queue.
        """
        task = self.task()
        db_url = db_url_from_request(self.request)
        try:
            kwargs = task.formfields2taskargs(self.request.json_body, db_url)
            taskresp = task.apply_async(kwargs=kwargs)
            result_url = self.request.route_path('result',
                                                 script=self.scriptid,
                                                 taskid=taskresp.id)
            return {'success': True, 'result': result_url}
        except Invalid as e:
            return {'success': False, 'msg': e.message}

    @view_config(route_name='state.json',
                 renderer='json',
                 request_method='GET')
    def statejson(self):
        """Returns state of current task as json

        Example:

        .. code-block:: javascript

            {
                "state": "PENDING",
                "ready": False,
                "success": False,
                "failure": False,
                "result": "/tool/calendar/b3c84d96-4dc7-4532-a864-3573202f202a"
            }

        """
        result = self.task_result()
        result_url = self.request.route_path('result',
                                             script=self.scriptid,
                                             taskid=result.id,
                                             )
        return {'state': result.state,
                'success': result.successful(),
                'failure': result.failed(),
                'ready': result.ready(),
                'result': result_url,
                }

    @view_config(renderer='state.mak', context=TaskNotReady)
    def statehtml(self):
        """Page shown when task is pending or running

        Page refreshes automagicly.
        Task can be canceled on page.
        """
        response = self.statejson()
        response['task'] = self.task()
        return response

    @view_config(route_name='state.json',
                 request_method='DELETE',
                 renderer='json')
    def revoke_task(self):
        """Cancel a pending or runnning task"""
        result = self.task_result()
        result.revoke(terminate=True)
        return {'success': True}

    def result_files(self):
        """Returns files of current result

        Returns dict with key is filename and value is url to file."""
        files = {}
        result_dir = self.task_result_directory()
        try:
            for filename in sorted(os.listdir(result_dir)):
                files[filename] = self.request.route_path(
                    'result_file',
                    script=self.scriptid,
                    taskid=self.taskid,
                    filename=filename)

        except OSError:
            logger.warn('Task {} resulted in no files'.format(self.taskid))
        return files

    @view_config(route_name='result', renderer='result.mak')
    def result(self):
        """Page with result

        When task.result_template is filled then
        returns page with rendered result_template.
        else
        returns page with listing of all result files.
        """
        task = self.task()
        result = self.task_result(True)
        files = self.result_files()
        result_html = task.render_result(result, files)

        data = {'task': task,
                'files': files,
                'result': result,
                'result_html': result_html,
                }
        return data

    @view_config(route_name='result_file')
    def result_file(self):
        """Returns file in result directory"""
        # results has files dict with key=base filename
        # and value is absolute path to file
        result_dir = self.task_result_directory()
        filename = self.request.matchdict['filename']
        path = os.path.join(result_dir, filename)
        return FileResponse(path, self.request)

    @view_config(route_name='trackers', renderer='json')
    def trackers(self):
        """List of trackers

        Each tracker has an id, project and species field.
        """
        Session = make_session_from_request(self.request)()

        q = Session.query(Tracker.device_info_serial,
                          TrackSession.key_name,
                          Individual.species,
                          )
        q = q.join(TrackSession).join(Individual)
        q = q.order_by(Tracker.device_info_serial).distinct()
        trackers = []
        for tid, project, species in q:
            trackers.append({'id': tid,
                             'project': project,
                             'species': species})

        Session.close()

        return trackers

    @view_config(route_name='species', renderer='json')
    def species(self):
        """List of species"""
        Session = make_session_from_request(self.request)()

        q = Session.query(Individual.species).distinct()
        q = q.order_by(Individual.species)
        species = []
        for speci in q:
            species.append({'id': speci, 'text': speci})

        Session.close()

        return species

    @view_config(route_name='projects', renderer='json')
    def projects(self):
        """List of projects"""
        Session = make_session_from_request(self.request)()

        q = Session.query(TrackSession.key_name).distinct()
        q = q.order_by(TrackSession.key_name)
        projects = []
        for pid in q:
            projects.append({'id': pid, 'text': pid})

        Session.close()

        return projects

    @view_config(route_name='tools', renderer='json')
    def tools(self):
        """List of all tasks available in script wrapper"""
        tools = []
        tasks = self.tasks()
        for task in sorted(tasks.values(), key=lambda task: task.name):
            form_url = self.request.route_path('apply', script=task.name)
            tools.append({
                'label': task.label,
                'form_url': form_url,
                'description': task.description,
                'made_by_researcher': task.made_by_researcher,
            })
        return tools
