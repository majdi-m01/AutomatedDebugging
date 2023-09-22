import ast
from textwrap import dedent
from typing import List
import unittest
from repair.tester import Record
from repair.synthesizer import *
from repair.benchmarks.utils import get_positive_tests, get_negative_tests

class TestFlip(unittest.TestCase):
    def flip_into(self, old: List[bool], new: List[bool]):
        synthesizer = Synthesizer(None, [], [])
        self.assertEqual(synthesizer.flip(old), new)

    def test_flip_empty(self):
        self.flip_into([], [])

    def test_flip_0(self):
        self.flip_into([False], [True])

    def test_flip_1(self):
        self.flip_into([True], [])

    def test_flip_000(self):
        self.flip_into([False, False, False], [False, False, True])

    def test_flip_111(self):
        self.flip_into([True, True, True], [])

    def test_flip_100(self):
        self.flip_into([True, False, False], [True, False, True])

    def test_flip_011(self):
        self.flip_into([False, True, True], [True])
        
    def test_flip_101011(self):
        self.flip_into([True, False, True, False, True, True], [True, False, True, True])

class TestSolveBasic(unittest.TestCase):
    def sat(self, constraints: Record):
        synthesizer = Synthesizer(None, [], [])
        is_sat = synthesizer.solve(constraints)
        self.assertTrue(is_sat)

    def unsat(self, constraints: Record):
        synthesizer = Synthesizer(None, [], [])
        is_sat = synthesizer.solve(constraints)
        self.assertFalse(is_sat)

    def test_solve_sat_1(self):
        self.sat(Record([False], [{'x': 1}])) # x != 1

    def test_solve_sat_2(self):
        self.sat(Record([True, False], [{'x': 1}, {'x': 2}])) # x == 1

    def test_solve_unsat_1(self):
        self.unsat(Record([True, False], [{'x': 1}, {'x': 1}]))
    
    def test_solve_unsat_2(self):
        self.unsat(Record([True, True], [{'x': 1}, {'x': 2}]))

    def test_solve_unsat_3(self):
        self.unsat(Record([False, False], [{'x': 1}, {'x': 2}]))

    def test_solve_sat_3(self):
        self.sat(Record([True, False], [{'x': 1, 'y': 'A'}, {'x': 1, 'y': 'B'}])) # y == 'A'
    
    def test_solve_sat_4(self):
        self.sat(Record([True, True], [{'x': 1, 'y': 'A'}, {'x': 2, 'y': 'A'}])) # y == 'A'

    def test_solve_sat_5(self):
        self.sat(Record([False, False], [{'x': 1, 'y': 'A'}, {'x': 2, 'y': 'A'}])) # y != 'A'

    def test_solve_sat_6(self):
        self.sat(Record([True, True, False],
                        [{'x': 1, 'y': 'B'}, {'x': 1, 'y': 'C'}, {'x': 1, 'y': 'A', 'z': 3}]))
        # y != 'A'
        
    def test_solve_unsat_4(self):
        self.unsat(Record([False, False, True],
                          [{'x': 1, 'y': 'A'}, {'x': 1, 'y': 'B'}, {'x': 1, 'y': 'A'}]))
class TestSolveTemplates(unittest.TestCase):
    def sat(self, constraints: Record, templates: Template | List[Template]):
        if isinstance(templates, Template):
            templates = [templates]

        synthesizer = Synthesizer(None, [], [], extra_templates=templates)
        is_sat = synthesizer.solve(constraints)
        self.assertTrue(is_sat)

    def unsat(self, constraints: Record, templates: Template | List[Template]):
        if isinstance(templates, Template):
            templates = [templates]

        synthesizer = Synthesizer(None, [], [], extra_templates=templates)
        is_sat = synthesizer.solve(constraints)
        self.assertFalse(is_sat)

    def test_solve_sat_nat(self):
        self.sat(Record([True, True, False, False], [{'x': 0}, {'x': 10}, {'x': -2}, {'x': -5}]),
                 Template.from_lambda('n: int => n >= 0'))
    
    def test_solve_sat_lt(self):
        self.sat(Record([True, False, True, False],
                        [{'x': 1, 'y': 2}, {'x': 4, 'y': 4}, {'x': 3, 'y': 4}, {'x': 5, 'y': 4}]),
                 Template.from_lambda('a: int, b: int => a < b'))
        
    def test_solve_unsat_le_ge(self):
        self.unsat(Record([True, False, True, False],
                          [{'x': 1, 'y': 2}, {'x': 4, 'y': 4}, {'x': 3, 'y': 4}, {'x': 5, 'y': 4}]),
                   [Template.from_lambda('a: int, b: int => a <= b'),
                    Template.from_lambda('a: int, b: int => a >= b')])
        
    def test_solve_sat_len(self):
        self.sat(Record([True, False, True, False],
                        [{'xs': [], 'y': 0}, {'xs': [1], 'y': 2}, {'xs': [1, 2], 'y': 2}, 
                         {'xs': [1, 2, 3], 'y': 2}]),
                 Template.from_lambda('(lst: list, k: int) => len(lst) == k'))
        
    def test_solve_sat_len_non_empty(self):
        self.sat(Record([False, False, True, False, True],
                        [{'xs': [], 'y': 0}, {'xs': [1], 'y': 2}, {'xs': [1, 2], 'y': 2}, 
                         {'xs': [1, 2, 3], 'y': 2}, {'xs': [1, 2, 3, 4], 'y': 4}]),
                 [Template.from_lambda('(lst: list, k: int) => len(lst) == k'),
                  Template.from_lambda('(lst: list, k: int) => k > 0 and len(lst) == k')])
        
    def test_solve_unsat_no_list_in_env(self):
        self.unsat(Record([False, False, True, False],
                          [{'y': 0}, {'xs': [1], 'y': 2}, {'xs': [1, 2], 'y': 2}, 
                           {'xs': [1, 2, 3], 'y': 2}]),
                   Template.from_lambda('(lst: list, k: int) => len(lst) == k'))
        
class TestSynthesizer(object): # mixin class
    abstract_code: str
    pos_tests: List[CodeType]
    neg_tests: List[CodeType]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        tree = ast.parse(dedent(cls.abstract_code))
        cls.synthesizer = Synthesizer(tree, cls.pos_tests, cls.neg_tests)
        cls.synthesizer.apply()
    
    def test_synthesize_success(self):
        self.assertIsNotNone(self.synthesizer.concrete_tree)

    def test_synthesize_correct(self):
        self.assertTrue(self.synthesizer.validate())

class TestSynthesizerCharIndex(TestSynthesizer, unittest.TestCase):
    abstract_code = """\
        def char_index(s: str, c: str):
            for i in range(len(s)):
                x = s[i]
                if x == c or __abstract__: # fix here
                    return i
    
            return None
    """

    from repair.benchmarks import char_index_tests
    pos_tests = get_positive_tests(char_index_tests)
    neg_tests = get_negative_tests(char_index_tests)

class TestSynthesizerListSum(TestSynthesizer, unittest.TestCase):
    abstract_code = """\
        def list_sum(xs):
            total = 0
            for x in xs:
                if not __abstract__:
                    total += x

            return total
    """

    from repair.benchmarks import list_sum_tests
    pos_tests = get_positive_tests(list_sum_tests)
    neg_tests = get_negative_tests(list_sum_tests)

class TestSynthesizerScanIntegers(TestSynthesizer, unittest.TestCase):
    abstract_code = """\
        def scan_integers(seq):
            scanned = []
            for value in seq:
                try:
                    int_value = int(value)
                except ValueError:
                    continue
                
                if __abstract__:
                    break
                scanned.append(int_value)

            return scanned
    """

    from repair.benchmarks import scan_integers_tests
    pos_tests = get_positive_tests(scan_integers_tests)
    neg_tests = get_negative_tests(scan_integers_tests)
