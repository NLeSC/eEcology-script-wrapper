from pyramid.config import Configurator

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    config.add_route('index', '/')
    config.add_route('apply', '/apply/{script}')
    config.add_route('status', '/status/{script}/{taskid}')
    config.add_route('result', '/result/{script}/{taskid}')

    config.scan()

    return config.make_wsgi_app()
