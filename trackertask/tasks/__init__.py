import os
import sys
import subprocess
from celery import Task
from celery import current_app
from celery.utils.log import get_task_logger
from sqlalchemy.engine.url import make_url
from sqlalchemy import engine_from_config
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage
import trackertask.models as models

logger = get_task_logger(__name__)

class PythonTask(Task):
    """Abstract task to run Python code"""
    abstract = True
    """Human readable label of task"""
    label = None
    """Description of task"""
    description = None
    """Filename of javascript form"""
    js_form = 'form.js'
    autoregister = True  # Change to False to hide this task

    @property
    def output_dir(self):
        directory = os.path.join(current_app.conf['task_output_directory'],
                                 self.request.id,
                                 )
        try:
            os.makedirs(directory)
        except OSError as e:
            if e.errno != 17:
                raise e

        return directory

    @property
    def task_dir(self):
        """Directory in which Task is defined

        Can be used to find location of Task resources like executables or javascript files.
        """
        return os.path.dirname(os.path.abspath(sys.modules[self.__module__].__file__))

    def formfields2taskargs(self, fields, db_url):
        """Validate and serialize form fields to dict.

        Used as kwargs for Task.run()

        If task requires db access it can add db_url to the task arguments.
        The db_url can be parsed and used to connect to db.

        eg. Python using sqlalchemy models::

            from trackertask.models import DBSession, Devices
            Session = DBSession(db_url)
            res = Session().query(Devices).all()
            Session.close_all()

        eg. For Matlab the SQLAlchemy URL has to be converted to JDBC
        In Python::

            from trackertask.models import make_url
            u = make_url(db_url)
            username = u.username
            password = u.password
            instance = u.database
            drivers = {'postgresql': 'org.postgresql.Driver'}
            driver = drivers[u.drivername]
            jdbc_url = 'jdbc:{drivername}://{host}:{port}/{database}'.format(drivername=u.drivername,
                                                                             host=u.host,
                                                                             port=u.port or 5432,
                                                                             database=u.database)
            if u.query.has_key('sslmode') and u.query['sslmode'] == 'require':
                jdbc_url += '?ssl=true'

        In Matlab::

            conn = database(instance, username, password, driver, jdbc_url)


        eg. For R
        In Python::

            from trackertask.models import make_url
            u = make_url(db_url)
            drivers = {'postgresql': 'PostgreSQL'}
            driver = drivers[u.drivername]
            dbname=u.database
            host = u.host
            port = u.port or 5432
            username = u.username
            password = u.password

        In R::

            drv <- dbDriver(driver)
            # TODO how to use sslmode=require in R, possibly via PGSSLMODE environment variable?
            con <- dbConnect(drv, dbname=dbname, host=host, port=port, user=username, password=password)
        """
        return fields

    @property
    def js_form_location(self):
        """Javascript to render ExtJS form to div with 'form' id"""
        return os.path.join(self.task_dir, self.js_form)


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
            self.octave.plot(output_dir, dsn, start, end, trackers)
            return {'output': '<output_dir>/plot.png'}

    """
    abstract = True
    octave_script = None

    def __init__(self):
        from oct2py import octave
        self.octave = octave

    def load_mfile(self):
        self.octave.addpath(os.path.join(self.task_dir, self.octave_script))


class SubProcessTask(PythonTask):
    """Abstract task to subprocess.Popen.

    Can execute any executable program with arguments.

    """
    abstract = True

    def pargs(self):
        """Arguments prepended to run(*args) which are used as Popen args"""
        return []

    def env(self):
        """Environment to use for subprocess.

        Defaults to current environment.

        Can be used to pass sensitive information to subprocess like database passwords.
        """
        return os.environ

    def run(self, *args):
        """
        Perform subprocess with self.pargs() and *args as arguments.

        Returns dict with following keys:
        - files, a dict of base-filenames and absolute paths.
        - return_code
        """
        pargs = self.pargs() + list(args)
        logger.warn(pargs)
        stdout_fn = os.path.join(self.output_dir, 'stdout.txt')
        stdout = open(stdout_fn, 'w')
        stderr_fn = os.path.join(self.output_dir, 'stderr.txt')
        stderr = open(stderr_fn, 'w')
        popen = subprocess.Popen(pargs,
                                 cwd=self.output_dir,
#                                 shell=True,
                                 env=self.env(),
                                 stdout=stdout,
                                 stderr=stderr,
                                 )
        return_code = popen.wait()

        files = {}
        files['stdout.txt'] = stdout_fn
        files['stderr.txt'] = stderr_fn

        return { 'files': files, 'return_code': return_code}


class MatlabTask(SubProcessTask):
    """Abstract task to execute compiled Matlab function

    eg.

    class PlotTask(MatlabTask):
        deploy_script = 'run_plot.sh'

        def run(self, output_dir, dsn, start, end, trackers):
            super(PlotTask, self).run([output_dir, dsn, start, end, trackers])
            return {'output': output_dir+'/plot.png'}

    Important!! Passing arguments containing spaces will fail.
    To fix in run_*.sh comment out the lines from args= to done
    and use "$@" instead of $args.
    """
    abstract = True
    _matlab = None
    """Matlab deployment script.
    During `mcc -vm -p googleearth script.m helper.m` an executable and deployment script is build.
    The executable is deployed or executed using the deployment script.
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
        p = super(MatlabTask, self).pargs()
        p += [os.path.join(self.task_dir, self.deploy_script),
              self.matlab,
              ]
        return p
