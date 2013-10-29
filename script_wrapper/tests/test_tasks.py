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

    @patch('os.listdir')
    def test_output_files(self, listdir):
        listdir.return_value = ['stderr.txt', 'stdout.txt']
        task = tasks.PythonTask()
        task.output_dir = Mock(return_value='/tmp/myjobdir')

        files = task.output_files()

        listdir.assert_called_with('/tmp/myjobdir')
        efiles = {'stderr.txt': '/tmp/myjobdir/stderr.txt',
                  'stdout.txt': '/tmp/myjobdir/stdout.txt'}
        self.assertEqual(files, efiles)


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
        task.app.conf['matlab.location'] = '/opt/matlab'

        self.assertEqual(task.matlab, '/opt/matlab')
        # matlab location from cache
        self.assertEqual(task.matlab, '/opt/matlab')

    def test_pargs(self):
        task = tasks.MatlabTask()
        task.app.conf['matlab.location'] = '/opt/matlab'
        task.script = 'runme.sh'

        taskdir = os.path.dirname(os.path.abspath(tasks.__file__))

        self.assertEqual(task.pargs(), [taskdir + '/runme.sh', '/opt/matlab'])

    def test_toNumberVectorString(self):
        task = tasks.MatlabTask()

        result = task.toNumberVectorString([1, 2, 3])
        eresult = '[1,2,3]'
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

        eresult = {'files': {
                             'stderr.txt': root_dir + '/stderr.txt',
                             'stdout.txt': root_dir + '/stdout.txt',
                             },
                   'return_code': 0}

        self.assertEqual(result, eresult)
        po.assert_called_with(['hostname'],
                              cwd=root_dir,
                              stdout=ANY, stderr=ANY,
                              env=ANY)

        import shutil
        shutil.rmtree(root_dir)
