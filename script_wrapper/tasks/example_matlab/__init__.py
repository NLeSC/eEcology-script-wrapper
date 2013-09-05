import os
import subprocess
from celery import Task
from celery import current_task
from celery.utils.log import get_task_logger
from script_wrapper.models import make_url
from script_wrapper.tasks import MatlabTask

logger = get_task_logger(__name__)

class ExampleMatlab(MatlabTask):
    name = 'examplematlab'
    label = 'Example in Matlab'
    description = 'Example in Matlab'
    """Perform a db query in a Matlab executable with postgresql query"""
    deploy_script = 'run_dbq.sh'

    def run(self, db_url, query):
        # TODO pass tracker_ids as '[1 2]' and in Matlab eval
        # See http://blogs.mathworks.com/loren/2011/01/06/matlab-data-types-as-arguments-to-standalone-applications/
        u = make_url(db_url)
        username = u.username
        password = u.password
        instance = u.database
        jdbc_url = 'jdbc:{drivername}://{host}:{port}/{database}'.format(drivername=u.drivername,
                                                                         host=u.host,
                                                                         port=u.port or 5432,
                                                                         database=u.database)

        # execute
        result = super(ExampleMatlab, self).run(username,
                                              password,
                                              instance,
                                              jdbc_url,
                                              query
                                              )

        # Add files in output dir to result set
        for fn in os.listdir(self.output_dir):
            result['files'][fn] = os.path.join(self.output_dir, fn)

        return result

    def formfields2taskargs(self, fields, db_url):
        return {'db_url':  db_url,
                'query': fields['query'],
                }