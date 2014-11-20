from celery.utils.log import get_task_logger
from script_wrapper.tasks import MatlabTask

logger = get_task_logger(__name__)


class OpenEarthDbQuery(MatlabTask):
    name = 'open_earth_db_query'
    label = "OpenEarth Database query"
    title = """Perform a db query in a Matlab executable
                  with postgresql query using OpenEarth toolkit"""
    script = 'run_test.sh'
    autoregister = False
    matlab_version = '2012b'

    def run(self, db_url):
        u = self.local_db_url(db_url)
        username = u.username
        password = u.password
        dbname = self.sslify_dbname(u)
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
