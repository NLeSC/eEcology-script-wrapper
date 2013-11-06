import unittest
from script_wrapper.tasks.pykml import PyKML

class Test(unittest.TestCase):
    def test_create_styles(self):
        task = PyKML()
        styles = task.create_styles()

        self.assertEqual(len(styles), 15)
