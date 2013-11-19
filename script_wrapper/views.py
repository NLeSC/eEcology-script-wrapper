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
from mako.template import Template
from pyramid.response import FileResponse
from pyramid.view import view_config
from script_wrapper.models import make_session_from_request
from script_wrapper.models import db_url_from_request
from script_wrapper.models import Device, Individual, TrackSession
from script_wrapper.validation import Invalid

logger = logging.getLogger(__package__)


class TaskNotReady(Exception):
    pass


class Views(object):
    def __init__(self, request):
        self.request = request
        self.celery = celery

    @property
    def scriptid(self):
        return self.request.matchdict['script']

    @property
    def taskid(self):
        return self.request.matchdict['taskid']

    def tasks(self):
        return {k: v for k, v in self.celery.tasks.iteritems()
                    if not k.startswith('celery.')}

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
        base = self.request.registry.settings['task_output_directory']
        directory = os.path.join(base, self.taskid)
        return directory

    @view_config(route_name='index', renderer='index.mak')
    def index(self):
        return {'tasks': self.tasks()}

    @view_config(route_name='apply', request_method='GET', renderer='form.mak')
    def form(self):
        task = self.tasks()[self.scriptid]
        return {'task': task}

    @view_config(route_name='jsform')
    def jsform(self):
        task = self.tasks()[self.scriptid]
        return FileResponse(task.js_form_location(), self.request)

    @view_config(route_name='apply', request_method='POST', renderer='json')
    def submit(self):
        task = self.tasks()[self.scriptid]
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
        response = self.statejson()
        response['task'] = self.tasks()[self.scriptid]
        return response

    @view_config(route_name='state.json',
                 request_method='DELETE',
                 renderer='json')
    def revoke_task(self):
        result = self.task_result()
        result.revoke(terminate=True)
        return {'success': True}

    @view_config(route_name='result', renderer='result.mak')
    def result(self):
        task = self.tasks()[self.scriptid]
        result = self.task_result(True)

        result_dir = self.task_result_directory()
        files = {}
        try:
            for filename in sorted(os.listdir(result_dir)):
                files[filename] = self.request.route_path('result_file',
                                                          script=task.name,
                                                          taskid=result.id,
                                                          filename=filename,
                                                          )
        except OSError:
            logger.warn('Task {} resulted in no files'.format(self.taskid))

        data = {
                'task': task,
                'files': files,
                'result': result,
                'query': result.result['query'],
                }
        if task.result_template is None:
            data['result_html'] = None
        else:
            template = Template(filename=task.result_template_location(), output_encoding='utf-8')
            data['result_html'] = template.render(**data)

        return data

    @view_config(route_name='result_file')
    def result_file(self):
        # results has files dict with key=base filename
        # and value is absolute path to file
        result_dir = self.task_result_directory()
        filename = self.request.matchdict['filename']
        path = os.path.join(result_dir, filename)
        return FileResponse(path, self.request)

    @view_config(route_name='trackers', renderer='json')
    def trackers(self):
        Session = make_session_from_request(self.request)()

        q = Session.query(Device.device_info_serial,
                          TrackSession.project_leader,
                          Individual.species,
                          )
        q = q.join(TrackSession).join(Individual)
        q = q.order_by(Device.device_info_serial).distinct()
        trackers = []
        for tid, project, species in q:
            trackers.append({'id': tid,
                             'project': project,
                             'species': species})

        Session.close()

        return trackers

    @view_config(route_name='species', renderer='json')
    def species(self):
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
        Session = make_session_from_request(self.request)()

        q = Session.query(TrackSession.project_leader).distinct()
        q = q.order_by(TrackSession.project_leader)
        projects = []
        for pid in q:
            projects.append({'id': pid, 'text': pid})

        Session.close()

        return projects
