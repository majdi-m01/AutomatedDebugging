import ast
import unittest
from repair.synthesizer import Template

class TestTemplate(unittest.TestCase):
    """These tests are not graded. They are used to test the template parser and instantiation."""
    def test_template_instantiate_1(self):
        t = Template.from_lambda('n: int => n >= 0')
        e = t.instantiate(['x'])
        self.assertEqual(ast.unparse(e), 'x >= 0')

    def test_template_instantiate_2(self):
        t = Template.from_lambda('x: int, y: int => x > y')
        e = t.instantiate(['v1', 'v2'])
        self.assertEqual(ast.unparse(e), 'v1 > v2')

    def test_template_instantiate_3(self):
        t = Template.from_lambda('(xs: list, k: int) => len(xs) > k and xs[k - 1] is not None')
        e = t.instantiate(['elements', 'alpha'])
        self.assertEqual(ast.unparse(e),
                         'len(elements) > alpha and elements[alpha - 1] is not None')