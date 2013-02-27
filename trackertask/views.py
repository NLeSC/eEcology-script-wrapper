import logging
from celery.result import AsyncResult
from celery import current_app as celery
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import FileResponse
from models import Devices, make_session_from_request, Individuals, TrackSession

logger = logging.getLogger(__package__)

def tasks():
    return {k : v for k, v in celery.tasks.iteritems()
                if not k.startswith('celery.')}

class Views(object):
    def __init__(self, request):
        self.request = request

    @property
    def scriptid(self):
        return self.request.matchdict['script']

    @property
    def taskid(self):
        return self.request.matchdict['taskid']

    @view_config(route_name='index', renderer='index.mak')
    def index(self):
        return {'tasks': tasks()}

    @view_config(route_name='apply', request_method='GET', renderer='form.mak')
    def form(self):
        task = tasks()[self.scriptid]
        return {'task': task}

    @view_config(route_name='jsform')
    def jsform(self):
        task = tasks()[self.scriptid]
        return FileResponse(task.js_form_location,
                            self.request,
                            content_type='application/x-javascript',
                            )

    @view_config(route_name='apply', request_method='POST', renderer='json')
    def submit(self):
        task = tasks()[self.scriptid]
        kwargs = task.formfields2taskargs(self.request.json_body)
        taskresp = task.apply_async(kwargs=kwargs)
        state_url = self.request.route_path('state',
                                        script=self.scriptid,
                                        taskid=taskresp.id)
        return {'success': True, 'state': state_url}


    @view_config(route_name='state.json', renderer='json')
    def statejson(self):
        result = AsyncResult(self.taskid)
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
        aresult = AsyncResult(self.taskid)
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
    def output(self):
        filename = self.request.matchdict['filename']
        aresult = AsyncResult(self.taskid)
        # results has files dict with key=base filename and value is absolute path to file
        path = aresult.result['files'][filename]
        return FileResponse(path, self.request)

    @view_config(route_name='trackers', renderer='json')
    def trackers(self):

        Session = make_session_from_request(self.request)

        q = Session().query(Devices.device_info_serial,
                                   Individuals.project_leader,
                                   Individuals.species).join(TrackSession)
        q = q.join(Individuals).order_by(Devices.device_info_serial)
        trackers = []
        for tid, leader, species in q:
            trackers.append({'id': tid, 'leader': leader, 'species': species})

        Session.close_all()

        return trackers
