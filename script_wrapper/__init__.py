# Copyright 2013 Netherlands eScience Center
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pyramid.config import Configurator
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.authentication import RemoteUserAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Allow, Authenticated, ALL_PERMISSIONS, DENY_ALL
from sqlalchemy import engine_from_config
from .version import __version__


class RootFactory(object):
    __acl__ = [(Allow, Authenticated, ALL_PERMISSIONS), DENY_ALL]

    def __init__(self, request):
        pass


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    config.set_root_factory(RootFactory)
    config.add_route('index', '/')
    config.add_route('trackers', '/trackers.json')
    config.add_route('species', '/species.json')
    config.add_route('projects', '/projects.json')
    config.add_route('tools', '/tools.json')
    config.add_route('jsform', '/tool/{script}/form.js')
    config.add_route('apply', '/tool/{script}/')
    config.add_route('state.json', '/tool/{script}/{taskid}.json')
    config.add_route('result', '/tool/{script}/{taskid}')
    config.add_route('result_file',
                     '/tool/{script}/{taskid}/{filename}')
    config.add_static_view('static',
                           'script_wrapper:static',
                           cache_max_age=3600)

    authen = RemoteUserAuthenticationPolicy('HTTP_REMOTE_USER')
    config.set_authentication_policy(authen)
    config.set_authorization_policy(ACLAuthorizationPolicy())

    config.include('pyramid_mako')

    config.scan()

    return config.make_wsgi_app()
