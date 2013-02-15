from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from celery.result import AsyncResult
from celery import current_app as celery
import logging
from .scripts import scripts

logger = logging.getLogger(__package__)


@view_config(route_name='index', renderer='index.mak')
def index(request):
    logger.info(celery.tasks)
    return {'scripts': scripts}

@view_config(route_name='apply', request_method='GET', renderer='form.mak')
def form(request):
    scriptid = request.matchdict['script']
    return {'script': scripts[scriptid]}

@view_config(route_name='apply', request_method='POST', renderer='json')
def submit(request):
    scriptid = request.matchdict['script']
    script = scripts[scriptid]
    task = script.task()
    kwargs = request.POST.mixed()
    # Add script specific configuration
    kwargs.update(script.args)
    logger.info(kwargs)
    taskresp = task.apply_async(kwargs=kwargs)
    return HTTPFound(location=request.route_path('status', script=scriptid, taskid=taskresp.id))

@view_config(route_name='status', renderer='json')
def status(request):
    scriptid = request.matchdict['script']
    taskid = request.matchdict['taskid']
    result = AsyncResult(taskid)
    if result.successful():
        return HTTPFound(location=request.route_path('result', script=scriptid, taskid=result.id))
    return {'state': result.state, 'result': result.result, 'script': scriptid,}

@view_config(route_name='result', renderer='json')
def result(request):
    scriptid = request.matchdict['script']
    taskid = request.matchdict['taskid']
    result = AsyncResult(taskid)
    return {'state': result.state, 'result': result.result, 'script': scriptid,}


