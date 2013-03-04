import os
import subprocess
from celery import Task
from celery import current_task
from celery.utils.log import get_task_logger
from trackertask.tasks import MatlabTask
from trackertask.models import make_url

logger = get_task_logger(__name__)

class OpenEarthDbQuery(MatlabTask):
    name = 'open_earth_db_query'
    label = "OpenEarth Database query"
    description = """Perform a db query in a Matlab executable with postgresql query using OpenEarth toolkit"""
    deploy_script = 'run_test.sh'
    # ui.grid.sara.nl has older matlab then rest of compilations
    _matlab = '/home/stefanv/MATLAB/MATLAB_Compiler_Runtime/v711'

    def run(self, db_url):
        u = make_url(db_url)
        username = u.username
        password = u.password
        dbname = u.database
        sslmode = u.query.get('sslmode', 'prefer')
        if sslmode == 'require':
            dbname += '?ssl=true'
#            dbname += '&sslfactory=org.postgresql.ssl.NonValidatingFactory'
        host = u.host

        # execute
        result = super(OpenEarthDbQuery, self).run(dbname,
                                                   host,
                                                   username,
                                                   password,
                                                   )

        return result

    def formfields2taskargs(self, fields, db_url):
        return {'db_url':  db_url,
                }