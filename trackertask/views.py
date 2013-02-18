from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import FileResponse
from celery.result import AsyncResult
from celery import current_app as celery
import logging

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

@view_config(route_name='apply', request_method='POST', renderer='json')
def submit(request):
    scriptid = request.matchdict['script']
    task = tasks()[scriptid]
    taskresp = task.apply_async(kwargs=task.formfields2taskargs(request.POST))
    return HTTPFound(location=request.route_path('status',
                                                 script=scriptid,
                                                 taskid=taskresp.id))

@view_config(route_name='status', renderer='json')
def status(request):
    scriptid = request.matchdict['script']
    taskid = request.matchdict['taskid']
    result = AsyncResult(taskid)
    if result.successful():
        return HTTPFound(location=request.route_path('result',
                                                     script=scriptid,
                                                     taskid=result.id,
                                                     ))
    return {'state': result.state,
            'result': result.result,
            'script': scriptid,
            }

@view_config(route_name='result', renderer='json')
def result(request):
    taskid = request.matchdict['taskid']
    result = AsyncResult(taskid).result
    return FileResponse(result['path'], request,
                        content_type=result['content_type'],
                        )

