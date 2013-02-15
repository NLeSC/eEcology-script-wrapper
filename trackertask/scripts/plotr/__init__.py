import logging
import tempfile
import os.path
from celery import Task
from celery import current_task
import rpy2.robjects as robjects
from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage
from trackertask.scripts import add_script
from trackertask.scripts import Script

logger = logging.getLogger(__package__)


class PlotR(Task):
    """Perform something in R"""
    _trackertask = None

    @property
    def trackertask(self):
        if self._trackertask is None:
            # TODO read from R file and make configurable
            r_string = """
            plotr <- function(output_file, title, start, end) {
                library(RSvgDevice)
                devSVG(file=output_file)
                plot(start:end,(-5:5)^2, type='b', main=title)
                dev.off()
            }
            """
            self._trackertask = SignatureTranslatedAnonymousPackage(r_string, 'trackertask')
        return self._trackertask

    def run(self, start, end, id, username, password):
        taskid = current_task.request.id
        output_fn = os.path.join(tempfile.gettempdir(), taskid+'.svg')
        self.trackertask.plotr(output_fn, id, int(start), int(end))
        return {'outputs': [{'text/svg': output_fn}]}


add_script(Script(id='plotr',
                  name='Plot overview using R',
                  description='Plots tracker measurements over time',
                  authors='Willem Bouten',
                  task=PlotR,
                  ))
