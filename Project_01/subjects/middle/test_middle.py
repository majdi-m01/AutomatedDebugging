import unittest
from middle import middle


class MiddleTests(unittest.TestCase):

    def test_335(self):
        self.assertEqual(3, middle(x=3, y=3, z=5))

    def test_123(self):
        self.assertEqual(2, middle(x=1, y=2, z=3))

    def test_321(self):
        self.assertEqual(2, middle(x=3, y=2, z=1))

    def test_555(self):
        self.assertEqual(5, middle(x=5, y=5, z=5))

    def test_534(self):
        self.assertEqual(4, middle(x=5, y=3, z=4))

    def test_213(self):
        self.assertEqual(2, middle(x=2, y=1, z=3))
