import unittest
from interpreter import interpret


class BFTests(unittest.TestCase):

    def test_increase_ptr(self):
        self.assertEqual(b'21', interpret(',>,.<.', b'12'))

    def test_increase_value(self):
        self.assertEqual(b'2', interpret(',+.', b'1'))

    def test_decrease_value(self):
        self.assertEqual(b'0', interpret(',-.', b'1'))
