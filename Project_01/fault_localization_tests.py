from debuggingbook.StatisticalDebugger import RankingDebugger

from fault_localization import Instrumenter, FaultLocalization
from slicer_statistical_debugging_tests import DebuggerTests


class FaultLocalizationTests(DebuggerTests):
    INSTRUMENTER_CLASS = Instrumenter

    def get_debugger(self, coverage=False) -> RankingDebugger:
        return FaultLocalization(self.instrumenter)

    def test_middle(self):
        debugger = self.middle_tester()
        self.assertIn(('middle', 6), debugger.rank()[:2])

    def test_remove_html_markup(self):
        debugger = self.remove_html_markup_tester()
        self.assertIn(('remove_html_markup', 11), debugger.rank()[:3])
        self.assertIn(('remove_html_markup', 12), debugger.rank()[:3])

    def test_sqrt(self):
        debugger = self.sqrt_tester()
        self.assertIn(('square_root', 6), debugger.rank()[:3])

    def test_bf(self):
        debugger = self.bf_tester()
        self.assertIn(('parse', 14), debugger.rank()[:5])
        self.assertIn(('parse', 15), debugger.rank()[:5])
