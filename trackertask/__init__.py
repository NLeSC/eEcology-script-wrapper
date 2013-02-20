from pyramid.config import Configurator
from sqlalchemy import engine_from_config
import models

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    config.add_route('index', '/')
    config.add_route('jsform', '/form/{script}.js')
    config.add_route('apply', '/apply/{script}')
    config.add_route('state', '/state/{script}/{taskid}')
    config.add_route('state.json', '/state/{script}/{taskid}.json')
    config.add_route('result', '/result/{script}/{taskid}')
    config.add_route('trackers', '/trackers.json')

    config.scan()

    engine = engine_from_config(settings, 'sqlalchemy.')
    models.DBSession.configure(bind=engine)
    models.reflect(bind=engine, schema=settings.get('reflect.schema'))

    import logging
    logger = logging.getLogger('trackertask')
    logger.info(models.meta.tables.__len__())
    logger.info(models.meta.tables.keys())

    return config.make_wsgi_app()
