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
        result['files'].append({'path': os.path.join(self.output_dir, 'out.kmz'),
                'name': 'out.kmz',
                'content_type': 'application/vnd.google-earth.kmz',
                })
        return result

    def formfields2taskargs(self, fields):
        return {}