import os
import subprocess
from celery import Task
from celery import current_task
from trackertask.tasks import MatlabTask

class KmzGen(MatlabTask):
    name = 'kmz_gen'
    label = "Generate KMZ file"
    description = """Uses Matlab google earth toolkit"""
    deploy_script = 'run_kmz_gen.sh'
    return_stderr = False
    return_stdout = False

    def run(self):
        result = super(KmzGen, self).run()
        result['files']['out.kmz'] = os.path.join(self.output_dir, 'out.kmz')
        return result

    def formfields2taskargs(self, fields, db_url):
        return {}