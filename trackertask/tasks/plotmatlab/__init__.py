import os
import subprocess
from celery import Task
from celery import current_task
from trackertask.tasks import MatlabTask

class PlotMatLab(MatlabTask):
    name = 'matlabplot'
    label = "Plot with Matlab"
    description = """Perform something in a Matlab executable"""
    deploy_script = 'run_plot.sh'

    def run(self, start, end, trackers, dsn):
            result = super(PlotMatLab, self).run([self.output_dir, dsn, start, end, trackers])
            result['files']['plot.png'] = os.path.join(self.output_dir, '/plot.png')
            return result
