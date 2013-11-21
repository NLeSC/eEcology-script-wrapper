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

import unittest
import os
from mock import patch, Mock, ANY
import script_wrapper.tasks as tasks


class TestPythonTask(unittest.TestCase):

    def test_js_form(self):
        task = tasks.PythonTask()
        self.assertEqual(task.js_form, 'form.js')

    def test_formfields2taskargs(self):

        task = tasks.PythonTask()

        ta = task.formfields2taskargs(1234, 5678)

        self.assertEqual(ta, 1234)

    def test_task_dir(self):
        task = tasks.PythonTask()
        tdir = task.task_dir()

        edir = os.path.dirname(os.path.abspath(tasks.__file__))
        self.assertEqual(tdir, edir)

    def test_js_form_location(self):
        task = tasks.PythonTask()
        edir = os.path.dirname(os.path.abspath(tasks.__file__))
        efn = os.path.join(edir, 'form.js')
        self.assertEqual(task.js_form_location(), efn)

    def test_output_dir(self):
        from tempfile import mkdtemp
        root_dir = mkdtemp()

        task = tasks.PythonTask()
        task.app.conf['task_output_directory'] = root_dir
        task.request.id = 'mytaskid'

        output_dir = task.output_dir()

        eoutput_dir = os.path.join(root_dir, 'mytaskid')
        self.assertEqual(output_dir, eoutput_dir)
        self.assertTrue(os.access(output_dir, os.R_OK))

        import shutil
        shutil.rmtree(root_dir)

    @patch('os.makedirs')
    def test_output_dir_DirExists_IgnoreException(self, makedirs):
        import errno
        makedirs.side_effect = OSError(errno.EEXIST, 'File exists')
        task = tasks.PythonTask()
        task.app.conf['task_output_directory'] = '/tmp'
        task.request.id = 'mytaskid'

        self.assertEqual(task.output_dir(), '/tmp/mytaskid')

    @patch('os.makedirs')
    def test_output_dir_PermissionDenied_Exception(self, makedirs):
        import errno
        makedirs.side_effect = OSError(errno.EPERM, 'Permission denied')
        task = tasks.PythonTask()
        task.app.conf['task_output_directory'] = '/etc'
        task.request.id = 'mytaskid'

        with self.assertRaises(OSError):
            task.output_dir()

    def test_local_db_url(self):
        task = tasks.PythonTask()
        task.app.conf['sqlalchemy.url'] = 'postgresql://localhost/eecology'
        db_url = 'postgresql://someone:somepw@somemachine/somedb'

        result = task.local_db_url(db_url)

        expected = 'postgresql://someone:somepw@localhost/eecology'
        self.assertEqual(str(result), expected)

    def test_sslify_dbname_nossl(self):
        task = tasks.PythonTask()
        from sqlalchemy.engine.url import make_url

        urls = ['postgresql://localhost/eecology',
                'postgresql://localhost/eecology?sslmode=disable',
                'postgresql://localhost/eecology?sslmode=prefer',
                'postgresql://localhost/eecology?sslmode=allow',
                ]
        for url in urls:
            db_url = make_url(url)
            db_name = task.sslify_dbname(db_url)
            exp = 'eecology'
            self.assertEqual(db_name, exp)

    def test_sslify_dbname_ssl(self):
        task = tasks.PythonTask()
        from sqlalchemy.engine.url import make_url

        urls = ['postgresql://localhost/eecology?sslmode=require',
                'postgresql://localhost/eecology?sslmode=verify',
                'postgresql://localhost/eecology?sslmode=verify-full',
                ]
        for url in urls:
            db_url = make_url(url)
            db_name = task.sslify_dbname(db_url)
            exp = 'eecology'
            exp += '?ssl=true&'
            exp += 'sslfactory=org.postgresql.ssl.NonValidatingFactory'
            self.assertEqual(db_name, exp)


class TestOctaveTask(unittest.TestCase):
    def test_load_mfile(self):
        task = tasks.OctaveTask()
        task.script = 'myscript.m'
        task.task_dir = Mock(return_value='/tmp/mydir')
        task.octave = Mock()

        task.load_mfile()

        task.octave.addpath.assert_called_with('/tmp/mydir/myscript.m')


class TestRTask(unittest.TestCase):

    def test_r_cached(self):
        task = tasks.RTask()
        task._r = 1234

        self.assertEqual(task.r, 1234)

    def test_toIntVector(self):
        task = tasks.RTask()

        result = task.toIntVector([1, 2, 3])

        from rpy2.robjects import IntVector
        self.assertIsInstance(result, IntVector)


class TestMatlabTask(unittest.TestCase):

    def test_matlab(self):
        task = tasks.MatlabTask()
        task.app.conf['matlab.location.2012a'] = '/opt/matlab'

        self.assertEqual(task.matlab, '/opt/matlab')
        # matlab location from cache
        self.assertEqual(task.matlab, '/opt/matlab')

    def test_pargs(self):
        task = tasks.MatlabTask()
        task.app.conf['matlab.location.2012a'] = '/opt/matlab'
        task.script = 'runme.sh'

        taskdir = os.path.dirname(os.path.abspath(tasks.__file__))

        self.assertEqual(task.pargs(), [taskdir + '/runme.sh', '/opt/matlab'])

    def test_list2vector_string(self):
        task = tasks.MatlabTask()

        result = task.list2vector_string([1, 2, 3])
        eresult = '[1,2,3]'
        self.assertEqual(result, eresult)

    def test_list2cell_array_string(self):
        task = tasks.MatlabTask()

        result = task.list2cell_array_string(['foo', 'bar'])
        eresult = "{'foo','bar'}"
        self.assertEqual(result, eresult)


class TestSubProcessTask(unittest.TestCase):

    def test_pargs(self):
        task = tasks.SubProcessTask()
        self.assertEqual(task.pargs(), [])

    @patch('subprocess.Popen')
    def test_run(self, po):

        from tempfile import mkdtemp
        root_dir = mkdtemp()
        task = tasks.SubProcessTask()
        task.output_dir = Mock(return_value=root_dir)
        po.return_value.wait.return_value = 0
        from os import getpid
        po.return_value.pid = getpid()

        result = task.run('hostname')

        eresult = {'return_code': 0}

        self.assertEqual(result, eresult)
        po.assert_called_with(['hostname'],
                              cwd=root_dir,
                              stdout=ANY, stderr=ANY,
                              preexec_fn=os.setsid,
                              env=ANY)

        import shutil
        shutil.rmtree(root_dir)

    @patch('subprocess.Popen')
    def test_run_unsuccessfull_return_code(self, po):
        from tempfile import mkdtemp
        root_dir = mkdtemp()
        task = tasks.SubProcessTask()
        task.output_dir = Mock(return_value=root_dir)
        po.return_value.wait.return_value = 1
        from os import getpid
        po.return_value.pid = getpid()

        with self.assertRaises(tasks.CalledProcessError) as e:
            task.run('/bin/false')

        self.assertEqual(e.exception.returncode, 1)
        self.assertEqual(e.exception.cmd, 'script')

        import shutil
        shutil.rmtree(root_dir)
