import logging
from celery.result import AsyncResult
from celery import current_app as celery
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import FileResponse
from pyramid.security import unauthenticated_userid
from models import make_session_from_request, db_url_from_request
from models import Device, Individual, TrackSession, Project

logger = logging.getLogger(__package__)

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
        return {k : v for k, v in self.celery.tasks.iteritems()
                    if not k.startswith('celery.')}

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
        return FileResponse(task.js_form_location,
                            self.request,
                            )

    @view_config(route_name='apply', request_method='POST', renderer='json')
    def submit(self):
        task = self.tasks()[self.scriptid]
        db_url = db_url_from_request(self.request)
        kwargs = task.formfields2taskargs(self.request.json_body, db_url)
        taskresp = task.apply_async(kwargs=kwargs)
        state_url = self.request.route_path('state',
                                        script=self.scriptid,
                                        taskid=taskresp.id)
        return {'success': True, 'state': state_url}


    @view_config(route_name='state.json', renderer='json')
    def statejson(self):
        result = self.celery.AsyncResult(self.taskid)
        result_url = self.request.route_path('result',
                                        script=self.scriptid,
                                        taskid=result.id,
                                        )
        return {'state': result.state,
                'success': result.successful(),
                'failure': result.failed(),
                'result': result_url,
                }

    @view_config(route_name='state', renderer='state.mak')
    def statehtml(self):
        response = self.statejson()
        if response['success'] or response['failure']:
            return HTTPFound(location=response['result'])
        return response

    def result_file_url(self, filename):
        return self.request.route_path('result_file',
                                  script=self.scriptid,
                                  taskid=self.taskid,
                                  filename=filename,
                                  )

    @view_config(route_name='result', renderer='result.mak')
    def result(self):
        aresult = self.celery.AsyncResult(self.taskid)
        result = aresult.result
        if aresult.failed():
            raise result

        if len(result['files']) == 1:
            first_fn = result['files'].keys()[0]
            return HTTPFound(location=self.result_file_url(first_fn))

        # replace local filesystem paths with urls to files
        files = {}
        for filename in result['files']:
            files[filename] = self.result_file_url(filename)

        return {'files': files}

    @view_config(route_name='result_file')
    def result_file(self):
        aresult = self.celery.AsyncResult(self.taskid)
        if aresult.failed():
            raise aresult.result
        # results has files dict with key=base filename and value is absolute path to file
        filename = self.request.matchdict['filename']
        path = aresult.result['files'][filename]
        return FileResponse(path, self.request)

    @view_config(route_name='trackers', renderer='json')
    def trackers(self):

        Session = make_session_from_request(self.request)()

        q = Session.query(Device.device_info_serial,
                            Project.common_name,
                            Individual.species,
                            )
        q = q.join(Project).join(TrackSession).join(Individual)
        q = q.order_by(Device.device_info_serial)
        trackers = []
        for tid, project, species in q:
            trackers.append({'id': tid, 'project': project, 'species': species})

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

        q = Session.query(Project.key_name, Project.common_name)
        q = q.join(Device)
        q = q.order_by(Project.common_name)
        projects = []
        for pid, text in q:
            projects.append({'id': pid, 'text': text})

        Session.close()

        return projects
