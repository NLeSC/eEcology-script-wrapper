import os
import sys
import subprocess
from celery import Task
from celery import current_app
from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage
from oct2py import octave

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

class PythonTask(Task):
    """Abstract task to run Python code"""
    abstract = True
    """Human readable label of task"""
    label = None
    """Description of task"""
    description = None
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = current_app.conf['sqlalchemy.url']
        return self._db

    @property
    def output_dir(self):
        directory = os.path.join(current_app.conf['task_output_directory'],
                                 self.request.id,
                                 )
        os.makedirs(directory)
        return directory

    @property
    def task_dir(self):
        return os.path.dirname(os.path.abspath(sys.modules[self.__module__].__file__))

    def formfields2taskargs(self, fields):
        """Validate and serialize form fields to dict.

        Used as kwargs for Task.run()"""
        return fields

    def formfields(self):
        """ExtJS form items list"""
        return []


class RTask(PythonTask):
    """Abstract task to run R function in a R-script file"""
    abstract = True
    r_script = None
    _r = None

    @property
    def r(self):
        """self.r_script is imported into R and it's functions are available as self.r.<function>"""
        if self._r is None:
            f = open(os.path.join(self.task_dir, self.r_script))
            r_string = f.read()
            f.close()
            self._r = SignatureTranslatedAnonymousPackage(r_string, 'r')
        return self._r


class OctaveTask(PythonTask):
    """Abstract task to run GNU Octave function in a octave script file

    eg.

    class PlotTask(OctaveTask):
        octave_script = 'plot.m'

        def run(self, output_dir, dsn, start, end, trackers):
            self.load_mfile()
            octave.plot(output_dir, dsn, start, end, trackers)
            return {'output': '<output_dir>/plot.png'}

    """
    abstract = True
    octave_script = None

    def load_mfile(self):
        octave.addpath(os.path.join(self.task_dir, self.octave_script))


class SubProcessTask(PythonTask):
    """Abstract task to subprocess.Popen.

    Can execute any executable program with arguments.

    """
    abstract = True

    def pargs(self):
        """Arguments prepended to run(*args) which are used as Popen args"""
        return []

    def run(self, *args, **kwargs):
        pargs = self.pargs() + args
        popen = subprocess.Popen(pargs,
                                 stderr=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 )
        (stdout, stderr) = popen.communicate()
        return {'returncode': popen.returncode,
                'stderr': stderr,
                'stdout': stdout,
                }


class MatlabTask(PythonTask):
    """Abstract task to execute compiled Matlab function

    eg.

    class PlotTask(MatlabTask):
        deploy_script = 'run_plot.sh'

        def run(self, output_dir, dsn, start, end, trackers):
            super(PlotTask, self).run([output_dir, dsn, start, end, trackers])
            return {'output': output_dir+'/plot.png'}

    """
    abstract = True
    _matlab = None
    """Matlab deployment script.
    During `mbuild` an executable and deployment script is build.
    The executable is deployed using the deployment script.
    """
    deploy_script = None

    @property
    def matlab(self):
        """Location of Matlab installation or
        location of Matlab compile runtime

        Fetched from celery config with 'matlab.location' key.
        """
        if self._matlab is None:
            self._matlab = current_app.conf['matlab.location']
        return self._matlab

    def pargs(self):
        """Prepend the deployment script and matlab location"""
        return ['/bin/sh',
                os.path.join(self.task_dir, self.deploy_script),
                self.matlab,
                ]

