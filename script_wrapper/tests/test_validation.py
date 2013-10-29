import unittest
import script_wrapper.validation as swv


class TestValidateRange(unittest.TestCase):

    def testInRange(self):
        self.assertTrue(swv.validateRange(5, 0, 10))

    def testTooLow(self):
        with self.assertRaises(swv.Invalid) as e:
            swv.validateRange(-5, 0, 10)
            self.assertEquals(e.message, 'No data points selected for this script, please increase or shift time range')

    def testTooHigh(self):
        with self.assertRaises(swv.Invalid) as e:
            swv.validateRange(15, 0, 10)
            self.assertEquals(e.message, 'Too many data points selected for this script, please reduce time range')
