import ast
import inspect
import unittest
from repair.benchmarks.utils import get_positive_tests, get_negative_tests
from repair.repairer import Repairer

class TestRepairer(unittest.TestCase):
    def repair(self, input_module, line_no: int, test_module):
        tree = ast.parse(inspect.getsource(input_module))

        pos_tests = get_positive_tests(test_module)
        neg_tests = get_negative_tests(test_module)

        log = False # enable log if you want to debug your repairer
        r = Repairer(tree, line_no, pos_tests, neg_tests, log=log)
        if log:
            print()
        self.assertTrue(r.repair())

        failures = []
        passed = r.validate(failures=failures)
        self.assertTrue(passed, f'test cases {failures} failed')

    def test_repair_char_index(self):
        from repair.benchmarks import char_index, char_index_tests
        self.repair(char_index, 9, char_index_tests)

    def test_repair_list_sum(self):
        from repair.benchmarks import list_sum, list_sum_tests
        self.repair(list_sum, 4, list_sum_tests)

    def test_repair_scan_integers(self):
        from repair.benchmarks import scan_integers, scan_integers_tests
        self.repair(scan_integers, 12, scan_integers_tests)

    def test_repair_scan_integers_alter(self):
        from repair.benchmarks import scan_integers, scan_integers_tests
        self.repair(scan_integers, 7, scan_integers_tests)