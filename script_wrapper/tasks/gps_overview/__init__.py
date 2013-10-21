import os
import subprocess
from celery import Task
from celery import current_task
from celery.utils.log import get_task_logger
from script_wrapper.tasks import MatlabTask
from script_wrapper.models import make_url

logger = get_task_logger(__name__)

class GpsOverview(MatlabTask):
    name = 'gps_overview'
    label = "GPS Overview"
    description = """Perform something in a Matlab executable with postgresql query"""
    deploy_script = 'run_gps_overview.sh'

    def env(self):
        env = super(GpsOverview, self).env()
        env['DB_PASSWORD'] = self.db_url.password
        return env

    def run(self, db_url, trackers):
        # prepare arguments
        tracker_ids = '[{}]'.format(' '.join([str(x) for x in trackers]))
        # TODO pass tracker_ids as '[1 2]' and in Matlab eval
        # See http://blogs.mathworks.com/loren/2011/01/06/matlab-data-types-as-arguments-to-standalone-applications/
        self.db_url = u = make_url(db_url)
        username = u.username
        password = u.password
        instance = u.database
        jdbc_url = 'jdbc:{drivername}://{host}:{port}/{database}'.format(drivername=u.drivername,
                                                                         host=u.host,
                                                                         port=u.port or 5432,
                                                                         database=u.database)

        # execute
        result = super(GpsOverview, self).run(username,
                                              password,
                                              instance,
                                              jdbc_url,
                                              tracker_ids
                                              )

        return result

    def formfields2taskargs(self, fields, db_url):
        return {'db_url':  db_url,
                'trackers': fields['trackers'],
                }