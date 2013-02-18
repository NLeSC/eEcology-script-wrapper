import logging
import tempfile
import os.path
from celery import Task
from celery import current_task
from trackertask.tasks import RTask

logger = logging.getLogger(__package__)


class PlotR(RTask):
    name = "plotr"
    label = "Plot in R"
    description = """Perform something in R"""
    r_script = 'plot.r'

    def run(self, start, end, tracker_id, username, password):
        output_fn = os.path.join(self.output_dir(),'plot.svg')
        self.r.plotr(output_fn, tracker_id, int(start), int(end))
        return {'outputs': [{'text/svg': output_fn}]}
