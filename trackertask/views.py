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
    status_url = request.route_path('status',
                                    script=scriptid,
                                    taskid=taskresp.id)
    return {'success': True, 'status': status_url}

@view_config(route_name='status.json', renderer='json')
@view_config(route_name='status', renderer='status.mak')
def status(request):
    scriptid = request.matchdict['script']
    taskid = request.matchdict['taskid']
    result = AsyncResult(taskid)
    result_url = request.route_path('result',
                                    script=scriptid,
                                    taskid=result.id,
                                    )
    return {'state': result.state,
            'success': result.successful(),
            'result': result_url
            }

@view_config(route_name='result')
def result(request):
    taskid = request.matchdict['taskid']
    result = AsyncResult(taskid).result
    return FileResponse(result['path'],
                        request,
                        content_type=result['content_type'],
                        )

@view_config(route_name='trackers', renderer='json')
def trackers(request):
    # TODO replace hardcoded list with db queries
    trackers = [
      {'id': 1, 'species': 'Gull'},
      {'id': 2, 'species': 'Gull'},
      {'id': 3, 'species': 'Gull'},
      {'id': 4, 'species': 'Gull'},
      {'id': 5, 'species': 'Gull'},
      {'id': 6, 'species': 'Gull'},
      {'id': 7, 'species': 'Gull'},
    ]
    return { 'trackers': trackers, 'total': len(trackers)}
