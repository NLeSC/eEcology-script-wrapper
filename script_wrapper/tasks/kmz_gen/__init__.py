import os
import subprocess
from celery import Task
from celery import current_task
from script_wrapper.tasks import MatlabTask

class KmzGen(MatlabTask):
    name = 'kmz_gen'
    label = "Generate KMZ file"
    description = """Uses Matlab google earth toolkit"""
    deploy_script = 'run_kmz_gen.sh'

    def run(self):
        result = super(KmzGen, self).run()
        result['files'] = {}  # Hide stderr.txt and stdout.txt
        result['files']['out.kmz'] = os.path.join(self.output_dir, 'out.kmz')
        return result

    def formfields2taskargs(self, fields, db_url):
        return {}