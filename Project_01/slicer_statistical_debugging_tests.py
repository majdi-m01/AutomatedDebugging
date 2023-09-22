import os.path
import re
import shutil
import subprocess
import unittest
from pathlib import Path

from debuggingbook.StatisticalDebugger import RankingDebugger

from slicer_statistical_debugging import Instrumenter, DependencyDebugger


class BaseTests(unittest.TestCase):
    TMP_PATH = Path('tmp')
    MIDDLE_PATH = Path('subjects', 'middle')
    MIDDLE_EXCLUDED = [Path('subjects', 'middle', 'test_middle.py')]
    REMOVE_HTML_MARKUP_PATH = Path('subjects', 'remove_html_markup')
    REMOVE_HTML_MARKUP_EXCLUDED = [Path('subjects', 'remove_html_markup', 'test_remove_html_markup.py')]
    SQRT_PATH = Path('subjects', 'sqrt')
    SQRT_EXCLUDED = [Path('subjects', 'sqrt', 'test_sqrt.py')]
    BF_PATH = Path('subjects', 'bf')
    BF_EXCLUDED = [Path('subjects', 'bf', 'test_bf.py'), Path('subjects', 'bf', 'language', '__init__.py')]
    INSTRUMENTER_CLASS = Instrumenter

    def instrument(self, source_directory, excluded_paths):
        self.instrumenter.instrument(source_directory=source_directory,
                                     dest_directory=self.TMP_PATH,
                                     excluded_paths=excluded_paths)

    def strip_empty_lines(self, path: Path):
        self.assertTrue(os.path.exists(path), f'{path} does not exist.')
        with open(path, 'r') as fp:
            content = fp.read()
        with open(path, 'w') as fp:
            fp.write(re.sub(r'\n(\s*\n)+', '\n', content))

    def instrument_middle(self):
        self.instrument(source_directory=self.MIDDLE_PATH, excluded_paths=self.MIDDLE_EXCLUDED)
        self.assertTrue(os.path.exists(self.TMP_PATH), 'Out directory `tmp` does not exist.')
        self.strip_empty_lines(self.TMP_PATH / 'middle.py')

    def instrument_remove_html_markup(self):
        self.instrument(source_directory=self.REMOVE_HTML_MARKUP_PATH, excluded_paths=self.REMOVE_HTML_MARKUP_EXCLUDED)
        self.assertTrue(os.path.exists(self.TMP_PATH), 'Out directory `tmp` does not exist.')
        self.strip_empty_lines(self.TMP_PATH / 'remove_html_markup.py')

    def instrument_sqrt(self):
        self.instrument(source_directory=self.SQRT_PATH, excluded_paths=self.SQRT_EXCLUDED)
        self.assertTrue(os.path.exists(self.TMP_PATH), 'Out directory `tmp` does not exist.')
        self.strip_empty_lines(self.TMP_PATH / 'sqrt.py')

    def instrument_bf(self):
        self.instrument(source_directory=self.BF_PATH, excluded_paths=self.BF_EXCLUDED)
        self.assertTrue(os.path.exists(self.TMP_PATH), 'Out directory `tmp` does not exist.')
        self.strip_empty_lines(self.TMP_PATH / 'interpreter.py')
        self.strip_empty_lines(self.TMP_PATH / 'language' / 'parser.py')

    def setUp(self) -> None:
        self.instrumenter = self.INSTRUMENTER_CLASS()

    def tearDown(self) -> None:
        shutil.rmtree(Path('tmp'), ignore_errors=True)


class InstrumentTests(BaseTests):

    def test_structure_middle(self):
        self.instrument_middle()
        self.assertTrue(os.path.exists(self.TMP_PATH / 'lib.py'), '`tmp/lib.py` does not exist.')
        self.assertTrue(os.path.exists(self.TMP_PATH / 'test_middle.py'), '`tmp/test_middle.py` does not exist.')

    def test_structure_remove_html_markup(self):
        self.instrument_remove_html_markup()
        self.assertTrue(os.path.exists(self.TMP_PATH / 'lib.py'), '`tmp/lib.py` does not exist.')
        self.assertTrue(os.path.exists(self.TMP_PATH / 'test_remove_html_markup.py'),
                        '`tmp/test_remove_html_markup.py` does not exist.')

    def test_structure_sqrt(self):
        self.instrument_sqrt()
        self.assertTrue(os.path.exists(self.TMP_PATH / 'lib.py'), '`tmp/lib.py` does not exist.')
        self.assertTrue(os.path.exists(self.TMP_PATH / 'test_sqrt.py'), '`tmp/test_sqrt.py` does not exist.')

    def test_structure_bf(self):
        self.instrument_bf()
        self.assertTrue(os.path.exists(os.path.join(self.TMP_PATH / 'lib.py')), '`tmp/lib.py` does not exist.')
        self.assertTrue(os.path.exists(os.path.join(self.TMP_PATH / 'language' / '__init__.py')),
                        '`tmp/language/__init__.py` does not exist.')
        self.assertTrue(os.path.exists(self.TMP_PATH / 'test_bf.py'), '`tmp/test_bf.py` does not exist.')


class DebuggerTests(BaseTests):

    def setUp(self) -> None:
        super().setUp()
        self.current_dir = Path.cwd()

    def tearDown(self) -> None:
        os.chdir(self.current_dir)
        super().tearDown()

    def get_debugger(self, coverage=False) -> RankingDebugger:
        return DependencyDebugger(coverage=coverage)

    def middle_tester(self, coverage=False) -> DependencyDebugger:
        self.instrument_middle()

        os.chdir(Path('tmp'))
        debugger = self.get_debugger(coverage=coverage)
        with debugger.collect_pass(Path('dump')):
            subprocess.run(['py', '-m', 'unittest', 'test_middle.MiddleTests.test_335'])
        with debugger.collect_pass(Path('dump')):
            subprocess.run(['py', '-m', 'unittest', 'test_middle.MiddleTests.test_123'])
        with debugger.collect_pass(Path('dump')):
            subprocess.run(['py', '-m', 'unittest', 'test_middle.MiddleTests.test_321'])
        with debugger.collect_pass(Path('dump')):
            subprocess.run(['py', '-m', 'unittest', 'test_middle.MiddleTests.test_555'])
        with debugger.collect_pass(Path('dump')):
            subprocess.run(['py', '-m', 'unittest', 'test_middle.MiddleTests.test_534'])
        with debugger.collect_fail(Path('dump')):
            subprocess.run(['py', '-m', 'unittest', 'test_middle.MiddleTests.test_213'])

        return debugger

    def remove_html_markup_tester(self, coverage=False) -> DependencyDebugger:
        self.instrument_remove_html_markup()

        os.chdir(Path('tmp'))
        debugger = self.get_debugger(coverage=coverage)
        with debugger.collect_pass(Path('dump')):
            subprocess.run(['py', '-m', 'unittest', 'test_remove_html_markup.RemoveHTMLMarkupTests.test_abc'])
        with debugger.collect_pass(Path('dump')):
            subprocess.run(
                ['py', '-m', 'unittest', 'test_remove_html_markup.RemoveHTMLMarkupTests.test_b_abc_b'])
        with debugger.collect_fail(Path('dump')):
            subprocess.run(
                ['py', '-m', 'unittest', 'test_remove_html_markup.RemoveHTMLMarkupTests.test_quoted_abc'])

        return debugger

    def sqrt_tester(self, coverage=False) -> DependencyDebugger:
        self.instrument_sqrt()

        os.chdir(Path('tmp'))
        debugger = self.get_debugger(coverage=coverage)
        with debugger.collect_pass(Path('dump')):
            subprocess.run(['py', '-m', 'unittest', 'test_sqrt.SqrtTests.test_9'])
        with debugger.collect_pass(Path('dump')):
            subprocess.run(['py', '-m', 'unittest', 'test_sqrt.SqrtTests.test_2'])
        with debugger.collect_fail(Path('dump')):
            subprocess.run(['py', '-m', 'unittest', 'test_sqrt.SqrtTests.test_neg_4'])

        return debugger

    def bf_tester(self, coverage=False) -> DependencyDebugger:
        self.instrument_bf()

        os.chdir(Path('tmp'))
        debugger = self.get_debugger(coverage=coverage)
        with debugger.collect_pass(Path('dump')):
            subprocess.run(['py', '-m', 'unittest', 'test_bf.BFTests.test_increase_ptr'])
        with debugger.collect_pass(Path('dump')):
            subprocess.run(['py', '-m', 'unittest', 'test_bf.BFTests.test_increase_value'])
        with debugger.collect_fail(Path('dump')):
            subprocess.run(['py', '-m', 'unittest', 'test_bf.BFTests.test_decrease_value'])

        return debugger


class DebuggerDependencyTests(DebuggerTests):

    def test_middle(self):
        debugger = self.middle_tester()

        results = {
            (('<middle() return value>', ('middle', 15)), (('<test>', ('middle', 13)),)): 0.8333333333333333,
            (('<middle() return value>', ('middle', 15)), (('y', ('middle', 4)),)): 0.8333333333333333,
            (('<test>', ('middle', 13)), (('<test>', ('middle', 8)),)): 0.7142857142857142,
            (('<test>', ('middle', 13)), (('x', ('middle', 3)), ('z', ('middle', 5)))): 0.7142857142857142,
            (('<test>', ('middle', 8)), (('<test>', ('middle', 6)),)): 0.625,
            (('<test>', ('middle', 8)), (('x', ('middle', 3)), ('y', ('middle', 4)))): 0.625,
            (('y', ('middle', 4)), ()): 0.5, (('x', ('middle', 3)), ()): 0.5, (('z', ('middle', 5)), ()): 0.5,
            (('<test>', ('middle', 6)), (('y', ('middle', 4)), ('z', ('middle', 5)))): 0.5,
            (('<test>', ('middle', 6)), ()): 0.5,
            (('<middle() return value>', ('middle', 26)), (('z', ('middle', 5)),)): 0.0,
            (('<test>', ('middle', 18)), (('x', ('middle', 3)), ('y', ('middle', 4)))): 0.0,
            (('<middle() return value>', ('middle', 10)), (('y', ('middle', 4)),)): 0.0,
            (('<middle() return value>', ('middle', 10)), (('<test>', ('middle', 8)),)): 0.0,
            (('<middle() return value>', ('middle', 20)), (('y', ('middle', 4)),)): 0.0,
            (('<middle() return value>', ('middle', 20)), (('<test>', ('middle', 18)),)): 0.0,
            (('<test>', ('middle', 23)), (('<test>', ('middle', 18)),)): 0.0,
            (('<test>', ('middle', 18)), (('<test>', ('middle', 6)),)): 0.0,
            (('<test>', ('middle', 23)), (('x', ('middle', 3)), ('z', ('middle', 5)))): 0.0,
            (('<middle() return value>', ('middle', 26)), ()): 0.0
        }

        for r in results:
            self.assertAlmostEqual(results[r], debugger.suspiciousness(r), delta=0.00001, msg=f'{r} is not correct')

    def test_remove_html_markup(self):
        debugger = self.remove_html_markup_tester()

        results = {
            (('quote', ('remove_html_markup', 20)),
             (('quote', ('remove_html_markup', 5)), ('quote', ('remove_html_markup', 20)))): 1.0,
            (('quote', ('remove_html_markup', 20)), (('<test>', ('remove_html_markup', 18)),)): 1.0,
            (('<test>', ('remove_html_markup', 8)), (('c', ('remove_html_markup', 7)),)): 0.6666666666666667,
            (('<test>', ('remove_html_markup', 13)), (('c', ('remove_html_markup', 7)),)): 0.6666666666666667,
            (('<test>', ('remove_html_markup', 23)), (('tag', ('remove_html_markup', 4)),)): 0.6666666666666667,
            (('tag', ('remove_html_markup', 4)), ()): 0.5,
            (('<remove_html_markup() return value>', ('remove_html_markup', 26)), ()): 0.5,
            (('<remove_html_markup() return value>', ('remove_html_markup', 26)),
             (('out', ('remove_html_markup', 25)),)): 0.5,
            (('out', ('remove_html_markup', 25)), (('<test>', ('remove_html_markup', 23)),)): 0.5,
            (('c', ('remove_html_markup', 7)), ()): 0.5, (('out', ('remove_html_markup', 6)), ()): 0.5,
            (('quote', ('remove_html_markup', 5)), ()): 0.5,
            (('<test>', ('remove_html_markup', 23)), (('<test>', ('remove_html_markup', 18)),)): 0.5,
            (('c', ('remove_html_markup', 7)), (('s', ('remove_html_markup', 3)),)): 0.5,
            (('<test>', ('remove_html_markup', 18)), (('<test>', ('remove_html_markup', 13)),)): 0.5,
            (('s', ('remove_html_markup', 3)), ()): 0.5,
            (('<test>', ('remove_html_markup', 13)), (('<test>', ('remove_html_markup', 8)),)): 0.5,
            (('<test>', ('remove_html_markup', 18)), (('c', ('remove_html_markup', 7)),)): 0.5,
            (('<test>', ('remove_html_markup', 8)), ()): 0.5,
            (('out', ('remove_html_markup', 25)),
             (('c', ('remove_html_markup', 7)), ('out', ('remove_html_markup', 6)),
              ('out', ('remove_html_markup', 25)))): 0.5,
            (('tag', ('remove_html_markup', 10)), (('<test>', ('remove_html_markup', 8)),)): 0.0,
            (('tag', ('remove_html_markup', 15)), ()): 0.0,
            (('<test>', ('remove_html_markup', 23)),
             (('tag', ('remove_html_markup', 10)), ('tag', ('remove_html_markup', 15)))): 0.0,
            (('tag', ('remove_html_markup', 15)), (('<test>', ('remove_html_markup', 13)),)): 0.0,
            (('<test>', ('remove_html_markup', 8)),
             (('c', ('remove_html_markup', 7)), ('quote', ('remove_html_markup', 5)))): 0.0,
            (('<test>', ('remove_html_markup', 13)),
             (('c', ('remove_html_markup', 7)), ('quote', ('remove_html_markup', 5)))): 0.0,
            (('tag', ('remove_html_markup', 10)), ()): 0.0
        }

        for r in results:
            self.assertAlmostEqual(results[r], debugger.suspiciousness(r), delta=0.00001, msg=f'{r} is not correct')

    def test_sqrt(self):
        debugger = self.sqrt_tester()

        results = {
            (('guess', ('square_root', 9)), (('approx', ('square_root', 8)), ('x', ('square_root', 3)))): 0.5,
            (('x', ('square_root', 3)), ()): 0.5,
            (('guess', ('square_root', 5)), ()): 0.5,
            (('<test>', ('square_root', 6)),
             (('approx', ('square_root', 4)), ('approx', ('square_root', 8)), ('guess', ('square_root', 5)),
              ('guess', ('square_root', 9)))): 0.5,
            (('guess', ('square_root', 5)), (('x', ('square_root', 3)),)): 0.5,
            (('<test>', ('square_root', 6)), ()): 0.5, (('approx', ('square_root', 4)), ()): 0.5,
            (('guess', ('square_root', 9)), (('<test>', ('square_root', 6)),)): 0.5,
            (('approx', ('square_root', 8)), (('guess', ('square_root', 5)), ('guess', ('square_root', 9)))): 0.5,
            (('approx', ('square_root', 8)), (('<test>', ('square_root', 6)),)): 0.5,
            (('<square_root() return value>', ('square_root', 10)), ()): 0.0,
            (('<square_root() return value>', ('square_root', 10)), (('approx', ('square_root', 8)),)): 0.0
        }

        for r in results:
            self.assertAlmostEqual(results[r], debugger.suspiciousness(r), delta=0.00001, msg=f'{r} is not correct')

    def test_bf(self):
        debugger = self.bf_tester()

        results = {
            (('<test>', ('interpret', 48)),
             (('mem', ('interpret', 16)), ('mem', ('interpret', 46)), ('ptr', ('interpret', 10)))): 0.6666666666666667,
            (('pos', ('interpret', 41)),
             (('mem', ('interpret', 16)), ('pos', ('interpret', 17)), ('ptr', ('interpret', 10)))): 0.6666666666666667,
            (('pos', ('interpret', 17)), (('pos', ('interpret', 47)),)): 0.6666666666666667,
            (('<test>', ('interpret', 44)),
             (('pos', ('interpret', 11)), ('token_string', ('interpret', 7)))): 0.6666666666666667,
            (('mem', ('interpret', 16)), (('mem', ('interpret', 46)), ('ptr', ('interpret', 10)))): 0.6666666666666667,
            (('<test>', ('interpret', 14)), (
            ('pos', ('interpret', 11)), ('pos', ('interpret', 17)), ('pos', ('interpret', 47)),
            ('token_string', ('interpret', 7)))): 0.6666666666666667,
            (('input_stream', ('interpret', 46)), (('input_stream', ('interpret', 6)), ('mem', ('interpret', 9)),
                                                   ('ptr', ('interpret', 10)))): 0.6666666666666667,
            (('<test>', ('interpret', 38)), (('pos', ('interpret', 11)), ('pos', ('interpret', 17)),
                                             ('token_string', ('interpret', 7)))): 0.6666666666666667,
            (('pos', ('interpret', 17)), (('<test>', ('interpret', 14)),)): 0.6666666666666667,
            (('mem', ('interpret', 16)), (('<test>', ('interpret', 14)),)): 0.6666666666666667,
            (('<test>', ('interpret', 26)), (('pos', ('interpret', 11)), ('pos', ('interpret', 17)),
                                             ('token_string', ('interpret', 7)))): 0.6666666666666667,
            (('<test>', ('interpret', 32)), (('pos', ('interpret', 11)), ('pos', ('interpret', 17)),
                                             ('token_string', ('interpret', 7)))): 0.6666666666666667,
            (('<test>', ('interpret', 12)), (
            ('pos', ('interpret', 11)), ('pos', ('interpret', 17)), ('pos', ('interpret', 41)),
            ('pos', ('interpret', 47)), ('token_string', ('interpret', 7)))): 0.6666666666666667,
            (('<test>', ('interpret', 20)), (('pos', ('interpret', 11)), ('pos', ('interpret', 17)),
                                             ('token_string', ('interpret', 7)))): 0.6666666666666667,
            (('<test>', ('interpret', 48)), (('<test>', ('interpret', 14)), ('<test>', ('interpret', 38)),
                                             ('<test>', ('interpret', 44)))): 0.6666666666666667,
            (('pos', ('interpret', 47)), (('pos', ('interpret', 11)),)): 0.6666666666666667,
            (('<parse() return value>', ('parse', 39)), ()): 0.5,
            (('<test>', ('parse', 8)), ()): 0.5,
            (('<test>', ('parse', 18)), (('c', ('parse', 7)),)): 0.5,
            (('<test>', ('parse', 33)), (('<test>', ('parse', 28)),)): 0.5,
            (('<interpret() return value>', ('interpret', 51)), (('output_stream', ('interpret', 8)),)): 0.5,
            (('<test>', ('parse', 23)), (('c', ('parse', 7)),)): 0.5,
            (('<parse() return value>', ('parse', 39)), (('token_string', ('parse', 6)),)): 0.5,
            (('pos', ('interpret', 11)), ()): 0.5,
            (('s', ('parse', 5)), ()): 0.5,
            (('<test>', ('parse', 28)), (('<test>', ('parse', 23)),)): 0.5,
            (('<test>', ('interpret', 44)), (('<test>', ('interpret', 38)),)): 0.5,
            (('output_stream', ('interpret', 8)), ()): 0.5,
            (('s', ('parse', 5)), (('program', ('interpret', 5)),)): 0.5,
            (('token_string', ('interpret', 7)), ()): 0.5,
            (('<test>', ('parse', 13)), (('<test>', ('parse', 8)),)): 0.5,
            (('<test>', ('parse', 8)), (('c', ('parse', 7)),)): 0.5,
            (('<test>', ('interpret', 38)), (('<test>', ('interpret', 32)),)): 0.5,
            (('<test>', ('parse', 28)), (('c', ('parse', 7)),)): 0.5,
            (('<test>', ('parse', 13)), (('c', ('parse', 7)),)): 0.5,
            (('<test>', ('interpret', 12)), ()): 0.5,
            (('<test>', ('interpret', 14)), (('<test>', ('interpret', 12)),)): 0.5,
            (('<test>', ('interpret', 26)), (('<test>', ('interpret', 20)),)): 0.5,
            (('<test>', ('parse', 23)), (('<test>', ('parse', 18)),)): 0.5,
            (('input_stream', ('interpret', 6)), ()): 0.5,
            (('<test>', ('interpret', 20)), (('<test>', ('interpret', 14)),)): 0.5,
            (('<test>', ('parse', 33)), (('c', ('parse', 7)),)): 0.5,
            (('token_string', ('parse', 6)), ()): 0.5,
            (('token_string', ('interpret', 7)), (('<parse() return value>', ('parse', 39)),)): 0.5,
            (('<test>', ('interpret', 32)), (('<test>', ('interpret', 26)),)): 0.5,
            (('pos', ('interpret', 47)), (('<test>', ('interpret', 44)),)): 0.5,
            (('mem', ('interpret', 9)), ()): 0.5,
            (('pos', ('interpret', 41)), (('<test>', ('interpret', 38)),)): 0.5,
            (('<interpret() return value>', ('interpret', 51)), ()): 0.5,
            (('mem', ('interpret', 46)), (('<test>', ('interpret', 44)),)): 0.5,
            (('c', ('parse', 7)), (('s', ('parse', 5)),)): 0.5,
            (('program', ('interpret', 5)), ()): 0.5,
            (('input_stream', ('interpret', 46)), (('<test>', ('interpret', 44)),)): 0.5,
            (('c', ('parse', 7)), ()): 0.5,
            (('ptr', ('interpret', 10)), ()): 0.5,
            (('mem', ('interpret', 46)), (('input_stream', ('interpret', 46)),)): 0.5,
            (('<test>', ('parse', 18)), (('<test>', ('parse', 13)),)): 0.5,
            (('<test>', ('interpret', 48)), (
            ('mem', ('interpret', 46)), ('ptr', ('interpret', 10)), ('ptr', ('interpret', 28)),
            ('ptr', ('interpret', 34)))): 0.0,
            (('<test>', ('interpret', 12)), (
            ('pos', ('interpret', 11)), ('pos', ('interpret', 29)), ('pos', ('interpret', 35)),
            ('pos', ('interpret', 41)), ('pos', ('interpret', 47)), ('token_string', ('interpret', 7)))): 0.0,
            (('<test>', ('interpret', 48)), (
            ('<test>', ('interpret', 26)), ('<test>', ('interpret', 32)), ('<test>', ('interpret', 38)),
            ('<test>', ('interpret', 44)))): 0.0,
            (('<test>', ('interpret', 32)), (
            ('pos', ('interpret', 11)), ('pos', ('interpret', 29)), ('pos', ('interpret', 35)),
            ('pos', ('interpret', 41)), ('pos', ('interpret', 47)), ('token_string', ('interpret', 7)))): 0.0,
            (('<test>', ('interpret', 20)), (
            ('pos', ('interpret', 11)), ('pos', ('interpret', 29)), ('pos', ('interpret', 35)),
            ('pos', ('interpret', 41)), ('pos', ('interpret', 47)), ('token_string', ('interpret', 7)))): 0.0,
            (('pos', ('interpret', 35)), (('<test>', ('interpret', 32)),)): 0.0,
            (('pos', ('interpret', 41)), (
            ('mem', ('interpret', 46)), ('pos', ('interpret', 35)), ('pos', ('interpret', 47)),
            ('ptr', ('interpret', 28)), ('ptr', ('interpret', 34)))): 0.0,
            (('input_stream', ('interpret', 46)), (
            ('input_stream', ('interpret', 6)), ('input_stream', ('interpret', 46)), ('mem', ('interpret', 9)),
            ('mem', ('interpret', 50)), ('ptr', ('interpret', 10)), ('ptr', ('interpret', 28)))): 0.0,
            (('mem', ('interpret', 50)), (('mem', ('interpret', 46)), ('ptr', ('interpret', 28)))): 0.0,
            (('ptr', ('interpret', 28)), (('ptr', ('interpret', 10)),)): 0.0,
            (('<test>', ('interpret', 14)), (
            ('pos', ('interpret', 11)), ('pos', ('interpret', 29)), ('pos', ('interpret', 35)),
            ('pos', ('interpret', 41)), ('pos', ('interpret', 47)), ('token_string', ('interpret', 7)))): 0.0,
            (('mem', ('interpret', 50)), (('<test>', ('interpret', 48)),)): 0.0,
            (('<test>', ('interpret', 38)), (
            ('pos', ('interpret', 11)), ('pos', ('interpret', 29)), ('pos', ('interpret', 35)),
            ('pos', ('interpret', 47)), ('token_string', ('interpret', 7)))): 0.0,
            (('ptr', ('interpret', 34)), (('ptr', ('interpret', 28)),)): 0.0,
            (('pos', ('interpret', 29)), (('pos', ('interpret', 47)),)): 0.0,
            (('pos', ('interpret', 35)), (('pos', ('interpret', 41)),)): 0.0,
            (('ptr', ('interpret', 28)), (('<test>', ('interpret', 26)),)): 0.0,
            (('pos', ('interpret', 29)), (('<test>', ('interpret', 26)),)): 0.0,
            (('ptr', ('interpret', 34)), (('<test>', ('interpret', 32)),)): 0.0,
            (('<test>', ('interpret', 26)), (
            ('pos', ('interpret', 11)), ('pos', ('interpret', 29)), ('pos', ('interpret', 35)),
            ('pos', ('interpret', 41)), ('pos', ('interpret', 47)), ('token_string', ('interpret', 7)))): 0.0,
            (('pos', ('interpret', 47)), (('pos', ('interpret', 11)), ('pos', ('interpret', 29)))): 0.0,
            (('<test>', ('interpret', 44)),
             (('pos', ('interpret', 11)), ('pos', ('interpret', 29)), ('token_string', ('interpret', 7)))): 0.0
        }

        rank = debugger.rank()

        self.assertEqual(79, len(rank))

        threshold = 0
        max_threshold = 3
        for r in results:
            s = debugger.suspiciousness(r)
            if s is None:
                threshold += 1
                self.assertLessEqual(threshold, max_threshold)
            else:
                self.assertAlmostEqual(results[r], s, delta=0.00001, msg=f'{r} is not correct')


class DebuggerRankingTests(DebuggerTests):

    def test_middle(self):
        debugger = self.middle_tester(coverage=True)
        try:
            self.assertIn(('middle', 15), debugger.rank()[:1])
        except AssertionError:
            self.assertIn(('middle', 6), debugger.rank()[:1])

    def test_remove_html_markup(self):
        debugger = self.remove_html_markup_tester(coverage=True)
        try:
            self.assertIn(('remove_html_markup', 20), debugger.rank()[:1])
        except AssertionError:
            self.assertIn(('remove_html_markup', 12), debugger.rank()[:1])

    def test_sqrt(self):
        debugger = self.sqrt_tester(coverage=True)
        try:
            self.assertIn(('square_root', 8), debugger.rank()[:6])
        except AssertionError:
            self.assertIn(('square_root', 6), debugger.rank()[:6])

    def test_bf(self):
        debugger = self.bf_tester(coverage=True)
        try:
            self.assertIn(('interpret', 16), debugger.rank()[:2])
            self.assertIn(('interpret', 17), debugger.rank()[:2])
        except AssertionError:
            self.assertIn(('interpret', 14), debugger.rank()[:2])
            self.assertIn(('interpret', 15), debugger.rank()[:2])
