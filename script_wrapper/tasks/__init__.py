# Copyright 2013 Netherlands eScience Center
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import errno
import os
import signal
import sys
import subprocess
from celery import Task
from celery.utils.log import get_task_logger
from rpy2.robjects import IntVector
from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage
from sqlalchemy.engine.url import make_url

logger = get_task_logger(__name__)


class PythonTask(Task):
    """Abstract task to run Python code

    Attributes:

    abstract : boolean
        Abstract classes are not registered,
        but are used as the base class for new task types.
    label : string
        Human readable label of task.
    description : string
        Description of task.
    autoregister : boolean
        If disabled this task won't be registered automatically.
    js_form : string
        Filename of javascript form.
    result_template: string
        Filename of Mako template to render the script results.
        With following variables available inside template:

          * `task`, that is task object or self
          * celery `result` object
          * `query`, same a run script response['query']
          * `files`, dictionary of with filename as key and url as value.

    """
    abstract = True
    label = None
    description = None
    js_form = 'form.js'
    result_template = None
    autoregister = True  # Change to False to hide this task

    def output_dir(self):
        """Directory where task can put output files.

        Combination of 'task_output_directory' config and task identifier.

        Directory will be created when it does not exist.
        """
        directory = os.path.join(self.app.conf['task_output_directory'],
                                 self.request.id,
                                 )
        try:
            os.makedirs(directory)
        except OSError as e:
            # ignore exception when it already exists
            if e.errno != errno.EEXIST:
                raise e

        return directory

    def local_db_url(self, db_url):
        worker_db_url = make_url(self.app.conf['sqlalchemy.url'])
        worker_db_url.username = db_url.username
        worker_db_url.password = db_url.password
        return worker_db_url

    def task_dir(self):
        """Directory in which Task is defined

        Can be used to find location of Task resources like executables.
        """
        this_file = os.path.abspath(sys.modules[self.__module__].__file__)
        return os.path.dirname(this_file)

    def formfields2taskargs(self, fields, db_url):
        """Validate and serialize form fields to dict which is passed to Task.run().

        Used as kwargs for Task.run()

        If task requires db access it can add db_url to the task arguments.
        The db_url can be parsed and used to connect to db.

        eg. Python using sqlalchemy models::

            from script_wrapper.models import DBSession, Devices
            Session = DBSession(db_url)
            res = Session().query(Devices).all()
            Session.close_all()

        eg. For Matlab the SQLAlchemy URL has to be converted to JDBC
        In Python::

            from script_wrapper.models import make_url
            u = make_url(db_url)
            username = u.username
            password = u.password
            instance = u.database
            drivers = {'postgresql': 'org.postgresql.Driver'}
            driver = drivers[u.drivername]
            jdbct = 'jdbc:{drivername}://{host}:{port}/{database}'
            jdbc_url = jdbct.format(drivername=u.drivername,
                                    host=u.host,
                                    port=u.port or 5432,
                                    database=u.database)
            if u.query.has_key('sslmode') and u.query['sslmode'] == 'require':
                jdbc_url += '?ssl=true'

        In Matlab::

            conn = database(instance, username, password, driver, jdbc_url)


        eg. For R
        In Python::

            from script_wrapper.models import make_url
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
            # TODO how to use sslmode=require in R,
            # possibly via PGSSLMODE environment variable?
            con <- dbConnect(drv, dbname=dbname, host=host, port=port,
                             user=username, password=password)

        Throw a script_wrapper.validation.Invalid exception when fields are not valid.
        """
        return fields

    def _abs_file_name(self, filename):
        return os.path.join(self.task_dir(), filename)

    def result_template_location(self):
        """Mako template to render result content"""
        return self._abs_file_name(self.result_template)

    def js_form_location(self):
        """Javascript to render ExtJS form to div with 'form' id"""
        return self._abs_file_name(self.js_form)

    def sslify_dbname(self, db_url):
        """To connect to postgresql database which requires ssl add query to db name."""
        db_name = db_url.database
        sslmodes = ['require', 'verify', 'verify-full']
        if 'sslmode' in db_url.query and db_url.query['sslmode'] in sslmodes:
            db_name += '?ssl=true&sslfactory=org.postgresql.ssl.NonValidatingFactory'
        return db_name


class RTask(PythonTask):
    """Abstract task to run R function in a R-script file

    Implementing this class requires you to override the script attribute
    and the ``run`` method, eg.::

        class PlotTask(RTask):
            script = 'plot.r'

            def run(self, output_dir()):
                self.load_mfile()
                self.r.plot(output_dir())
                return {'query': {}}

    Attributes:

    script : string
        Filename of R script with a function.

    """
    abstract = True
    script = None
    _r = None

    @property
    def r(self):
        """self.r_script is imported into R
        and it's functions are available as self.r.<function>"""
        if self._r is None:
            f = open(os.path.join(self.task_dir(), self.script))
            r_string = f.read()
            f.close()
            self._r = SignatureTranslatedAnonymousPackage(r_string, 'r')
        return self._r

    def toIntVector(self, myints):
        """Convert Python list of ints into a R Int vector"""
        return IntVector(myints)


class OctaveTask(PythonTask):
    """Abstract task to run GNU Octave function in a octave script file

    Implementing this class requires you to override the script attribute
    and the ``run`` method, eg.::

        class PlotTask(OctaveTask):
            script = 'plot.m'

            def run(self, output_dir()):
                self.load_mfile()
                self.octave.plot(output_dir())
                return {'query': {}}

    Attributes:

    script : string
        Filename of octave script with a function.
    """
    abstract = True
    script = None

    def __init__(self):
        from oct2py import octave
        self.octave = octave

    def load_mfile(self):
        """Add self.script to Octave path"""
        self.octave.addpath(os.path.join(self.task_dir(), self.script))

class CalledProcessError(Exception):
    def __init__(self, returncode, cmd):
        self.returncode = returncode
        self.cmd = cmd
        Exception.__init__(self, self.__str__())

    def __str__(self):
        return "Command '{}' returned non-zero exit status {}".format(self.cmd, self.returncode)

class SubProcessTask(PythonTask):
    """Abstract task to subprocess.Popen.

    Writes standard out to `stdout.txt` file and standard error to `stderr.txt` file.

    Can execute any executable program with arguments.

    Raises subprocess.CalledProcessError when subprocess returns non-zero exit status.
    """
    abstract = True

    def pargs(self):
        """Arguments prepended to run(\*args) which are used as Popen args"""
        return []

    def env(self):
        """Environment to use for subprocess.

        Defaults to current environment.

        Can be used to pass sensitive information to subprocess like passwords.
        """
        return os.environ

    def run(self, *args):
        """Perform subprocess with self.pargs() and \*args list as arguments.

        Returns dict with following keys:

        * files, a dict of base-filenames and absolute paths.
        * return_code
        """
        mypid = None
        pargs = self.pargs() + list(args)
        # Make sure all arguments are strings
        pargs = [str(parg) for parg in pargs]
        stdout_fn = os.path.join(self.output_dir(), 'stdout.txt')
        stdout = open(stdout_fn, 'w')
        stderr_fn = os.path.join(self.output_dir(), 'stderr.txt')
        stderr = open(stderr_fn, 'w')

        # When the task is revoked the children of the subprocess will keep running
        # To make sure the children are also killed use the process group id
        # To kill the process group id the term signal has to be redirected

        oldsignal = signal.getsignal(signal.SIGTERM)

        def cleanup():
            """Close output files and revert term signal"""
            stderr.close()
            stdout.close()
            signal.signal(signal.SIGTERM, oldsignal)

        def killit(signum, frame):
            """Kill the current process group and cleanup"""
            logger.warn('Killing pg {} of pid {} with signal {}'.format(os.getpgid(mypid), mypid, signum))
            os.killpg(os.getpgid(mypid), signum)
            cleanup()

        signal.signal(signal.SIGTERM, killit)

        popen = subprocess.Popen(pargs,
                                 cwd=self.output_dir(),
                                 env=self.env(),
                                 stdout=stdout,
                                 stderr=stderr,
                                 # starts subprocess in own process group
                                 # whole group can be killed when task is revoked
                                 preexec_fn=os.setsid,
                                 )
        self.update_state(state='RUNNING')
        mypid = popen.pid
        return_code = popen.wait()

        cleanup()

        if return_code is not 0:
            raise CalledProcessError(return_code, 'script')

        return {'return_code': return_code}


class MatlabTask(SubProcessTask):
    """Abstract task to execute compiled Matlab function

    Implementing this class requires you to override the script attribute
    and the ``run`` method, eg.::

        class PlotTask(MatlabTask):
            script = 'run_plot.sh'

            def run(self, output_dir()):
                result = super(PlotTask, self).run(output_dir())
                return result

    Attributes:

    script : string
        Filename of Matlab deployment script.
        During `mcc -vm plot.m` an executable and deployment script is build.
        The executable is executed using the script.
        Eg. Matlab script `plot.m` will be runnable by running `run_plot.sh`.

    """
    abstract = True
    _matlab = None
    script = None
    matlab_version = '2012a'

    @property
    def matlab(self):
        """Location of Matlab installation or
        location of Matlab compile runtime

        Fetched from celery config with 'matlab.location' key.
        """
        if self._matlab is None:
            self._matlab = self.app.conf['matlab.location.' + self.matlab_version]
        return self._matlab

    def pargs(self):
        """Prepend the deployment script and matlab location"""
        p = super(MatlabTask, self).pargs()
        p += [os.path.join(self.task_dir(), self.script),
              self.matlab,
              ]
        return p

    def list2vector_string(self, mylist):
        """Convers list into Matlab vector

        eg. x = [1,2,3] becomes '[1,2,3]'
        """
        return '[{}]'.format(",".join([str(i) for i in mylist]))

    def list2cell_array_string(self, mylist):
        """Convers list into Matlab vector

        eg. x = ['foo', 'bar'] becomes '{foo,bar}'
        """
        return '{{{}}}'.format(",".join(["'{}'".format(i) for i in mylist]))
