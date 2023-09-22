import unittest
from sqrt import square_root


class SqrtTests(unittest.TestCase):

    def test_9(self):
        self.assertAlmostEqual(3, square_root(9), delta=0.00001)

    def test_2(self):
        self.assertAlmostEqual(1.41421356237, square_root(2), delta=0.00001)

    def test_neg_4(self):
        try:
            square_root(-4)
        except ZeroDivisionError:
            self.fail('ZeroDivisionError was raised')
