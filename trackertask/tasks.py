from celery import Task
from celery import current_task
import time
import logging
import rpy2.robjects as robjects
from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage
import subprocess
import StringIO

logger = logging.getLogger(__package__)


class Plot(Task):
    def run(self, start, end, id, username, password):
        for i in xrange(int(end)):
            current_task.update_state(state='PROGRESS',
                meta={'current': i, 'total': end})
            time.sleep(float(start))
        return 'fancy plot of {} from {} to {}'.format(id, start, end)


class PlotR(Task):
    _trackertask = None

    @property
    def trackertask(self):
        if self._trackertask is None:
            # TODO read R file
            r_string = """
            plotr <- function(output_file) {
                library(RSvgDevice)
                devSVG(file=output_file)
                plot(1:11,(-5:5)^2, type='b', main='Simple')
                dev.off()
            }
            """
            self._trackertask = SignatureTranslatedAnonymousPackage(r_string, 'trackertask')
        return self._trackertask

    def run(self, start, end, id, username, password):
        self.trackertask.plotr(id)
        return id


class PlotMatLab(Task):
    def run(self, start, end, id, username, password):
        current_task.update_state(state='PROGRESS')
        args = ['/bin/sh',
                '/tmp/sw/run_stefan.sh',
                '/home/stefanv/MATLAB/MATLAB_Compiler_Runtime/v717',
                username,
                password,
                ]
        popen = subprocess.Popen(args,
                                      stderr=subprocess.PIPE,
                                      stdout=subprocess.PIPE)
        (stdout, stderr) = popen.communicate()
        return {'returncode': popen.returncode,
                'stderr': stderr,
                'stdout': stdout,
                }

