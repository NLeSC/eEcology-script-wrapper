import logging
from celery.result import AsyncResult
from celery import current_app as celery
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import FileResponse
import models

logger = logging.getLogger(__package__)

def tasks():
    return {k : v for k, v in celery.tasks.iteritems()
                if not k.startswith('celery.')}

@view_config(route_name='index', renderer='index.mak')
def index(request):
    return {'tasks': tasks()}

@view_config(route_name='apply', request_method='GET', renderer='form.mak')
def form(request):
    scriptid = request.matchdict['script']
    task = tasks()[scriptid]
    return {'task': task}

@view_config(route_name='jsform')
def jsform(request):
    scriptid = request.matchdict['script']
    task = tasks()[scriptid]
    return FileResponse(task.js_form_location,
                        request,
                        content_type='application/x-javascript',
                        )

@view_config(route_name='apply', request_method='POST', renderer='json')
def submit(request):
    scriptid = request.matchdict['script']
    task = tasks()[scriptid]
    kwargs = task.formfields2taskargs(request.json_body)
    taskresp = task.apply_async(kwargs=kwargs)
    state_url = request.route_path('state',
                                    script=scriptid,
                                    taskid=taskresp.id)
    return {'success': True, 'state': state_url}


@view_config(route_name='state.json', renderer='json')
def statejson(request):
    scriptid = request.matchdict['script']
    taskid = request.matchdict['taskid']
    result = AsyncResult(taskid)
    result_url = request.route_path('result',
                                    script=scriptid,
                                    taskid=result.id,
                                    )
    return {'state': result.state,
            'success': result.successful(),
            'failure': result.failed(),
            'result': result_url,
            }

@view_config(route_name='state', renderer='state.mak')
def statehtml(request):
    response = statejson(request)
    if response['success'] or response['failure']:
        return HTTPFound(location=response['result'])
    return response

@view_config(route_name='result')
def result(request):
    taskid = request.matchdict['taskid']
    aresult = AsyncResult(taskid)
    result = aresult.result
    if aresult.failed():
        raise result
    return FileResponse(result['path'],
                        request,
                        content_type=result['content_type'],
                        )

@view_config(route_name='trackers', renderer='json')
def trackers(request):
    return models.trackers()
