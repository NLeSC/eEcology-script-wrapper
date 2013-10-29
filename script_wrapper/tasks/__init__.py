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
import subprocess
import sys
from celery import Task
from celery.utils.log import get_task_logger
import iso8601
from sqlalchemy.engine.url import make_url
from sqlalchemy import engine_from_config
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from rpy2 import robjects
from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage
import script_wrapper.models as models

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
    output_dir : string
        Directory where task can put output files.

    """

    abstract = True
    label = None
    description = None
    js_form = 'form.js'
    autoregister = True  # Change to False to hide this task

    @property
    def output_dir(self):
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
        """
        return fields

    @property
    def js_form_location(self):
        """Javascript to render ExtJS form to div with 'form' id"""
        return os.path.join(self.task_dir(), self.js_form)

    def outputFiles(self):
        """Returns dict of all files in the output dir"""
        result = {}
        for fn in os.listdir(self.output_dir):
            result[fn] = os.path.join(self.output_dir, fn)
        return result


class RTask(PythonTask):
    """Abstract task to run R function in a R-script file

    Implementing this class requires you to override the script attribute
    and the ``run`` method, eg.::

        class PlotTask(RTask):
            script = 'plot.r'

            def run(self, output_dir):
                self.load_mfile()
                self.r.plot(output_dir)
                return {'plot.png': os.path.join(self.output_dir, 'plot.png')}

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
        return robjects.IntVector(myints)


class OctaveTask(PythonTask):
    """Abstract task to run GNU Octave function in a octave script file

    Implementing this class requires you to override the script attribute
    and the ``run`` method, eg.::

        class PlotTask(OctaveTask):
            script = 'plot.m'

            def run(self, output_dir):
                self.load_mfile()
                self.octave.plot(output_dir)
                return {'plot.png': os.path.join(self.output_dir, 'plot.png')}

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


class SubProcessTask(PythonTask):
    """Abstract task to subprocess.Popen.

    Can execute any executable program with arguments.

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
        """Perform subprocess with self.pargs() and *args as arguments.

        Returns dict with following keys:
        - files, a dict of base-filenames and absolute paths.
        - return_code
        """
        pargs = self.pargs() + list(args)
        stdout_fn = os.path.join(self.output_dir, 'stdout.txt')
        stdout = open(stdout_fn, 'w')
        stderr_fn = os.path.join(self.output_dir, 'stderr.txt')
        stderr = open(stderr_fn, 'w')
        popen = subprocess.Popen(pargs,
                                 cwd=self.output_dir,
                                 env=self.env(),
                                 stdout=stdout,
                                 stderr=stderr,
                                 )
        return_code = popen.wait()

        files = {}
        files['stdout.txt'] = stdout_fn
        files['stderr.txt'] = stderr_fn

        return {'files': files, 'return_code': return_code}


class MatlabTask(SubProcessTask):
    """Abstract task to execute compiled Matlab function

    Implementing this class requires you to override the script attribute
    and the ``run`` method, eg.::

        class PlotTask(MatlabTask):
            script = 'run_plot.sh'

            def run(self, output_dir):
                result = super(PlotTask, self).run(output_dir)
                abs_path = os.path.join(self.output_dir, 'plot.png')
                result['files']['plot.png'] = abs_path
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

    @property
    def matlab(self):
        """Location of Matlab installation or
        location of Matlab compile runtime

        Fetched from celery config with 'matlab.location' key.
        """
        if self._matlab is None:
            self._matlab = self.app.conf['matlab.location']
        return self._matlab

    def pargs(self):
        """Prepend the deployment script and matlab location"""
        p = super(MatlabTask, self).pargs()
        p += [os.path.join(self.task_dir(), self.script),
              self.matlab,
              ]
        return p

    def toNumberVectorString(self, mylist):
        """Convers list into Matlab vector

        eg. x = [1,2,3] becomes '[1,2,3]'
        """
        return '[{}]'.format(",".join([str(i) for i in mylist]))
