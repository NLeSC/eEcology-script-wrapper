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

def result_file_url(request, filename):
    return request.route_path('result_file',
                              script=request.matchdict['script'],
                              taskid=request.matchdict['taskid'],
                              filename=filename,
                              )

@view_config(route_name='result', renderer='result.mak')
def result(request):
    taskid = request.matchdict['taskid']
    aresult = AsyncResult(taskid)
    result = aresult.result
    if aresult.failed():
        raise result

    if len(result['files']) == 1:
        first_fn = result['files'].keys()[0]
        return HTTPFound(location=result_file_url(request, first_fn))

    # replace local filesystem paths with urls to files
    files = {}
    for filename in result['files']:
        files[filename] = result_file_url(request, filename)

    return {'files': files}

@view_config(route_name='result_file')
def output(request):
    taskid = request.matchdict['taskid']
    filename = request.matchdict['filename']
    aresult = AsyncResult(taskid)
    # results has files dict with key=base filename and value is absolute path to file
    path = aresult.result['files'][filename]
    return FileResponse(path, request)

@view_config(route_name='trackers', renderer='json')
def trackers(request):
    return models.trackers()
