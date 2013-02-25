from pyramid.config import Configurator
from sqlalchemy import engine_from_config
import models

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    config.add_route('index', '/')
    config.add_route('trackers', '/trackers.json')
    config.add_route('jsform', '/tool/{script}/form.js')
    config.add_route('apply', '/tool/{script}/')
    config.add_route('state.json', '/tool/{script}/{taskid}/state.json')
    config.add_route('state', '/tool/{script}/{taskid}/state')
    config.add_route('result', '/tool/{script}/{taskid}/result')
    config.add_route('output', '/tool/{script}/{taskid}/file/{fileindex}')
    config.add_static_view('static', 'trackertask:static', cache_max_age=3600)

    config.scan()

    engine = engine_from_config(settings, 'sqlalchemy.')
    models.DBSession.configure(bind=engine)
    models.reflect(bind=engine, schema=settings.get('reflect.schema'))

    return config.make_wsgi_app()
