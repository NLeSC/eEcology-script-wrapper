import unittest
import os
import sys
from mock import patch, Mock
from celery import Celery
import trackertask.tasks as tasks


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
        tdir = task.task_dir

        edir = os.path.dirname(os.path.abspath(tasks.__file__))
        self.assertEqual(tdir, edir)

    def test_js_form_location(self):
        task = tasks.PythonTask()
        edir = os.path.dirname(os.path.abspath(tasks.__file__))
        efn = os.path.join(edir, 'form.js')
        self.assertEqual(task.js_form_location, efn)

    def test_output_dir(self):
        from tempfile import mkdtemp
        root_dir = mkdtemp()

        task = tasks.PythonTask()
        task.app.conf['task_output_directory'] = root_dir
        task.request.id = 'mytaskid'

        output_dir = task.output_dir

        eoutput_dir = os.path.join(root_dir, 'mytaskid')
        self.assertEqual(output_dir, eoutput_dir)
        self.assertTrue(os.access(output_dir, os.R_OK))

        import shutil
        shutil.rmtree(root_dir)


