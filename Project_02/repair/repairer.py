import ast
from types import CodeType
from typing import List

from repair.mutator import Mutator
from repair.synthesizer import Synthesizer, Template
from repair.tester import run_tests

class Repairer:
    def __init__(self, tree: ast.Module, line_no: int,
                 passing_tests: List[CodeType], failing_tests: List[CodeType],
                 k: int = 10, extra_templates: List[Template] = None, log: bool = False) -> None:
        self.old_tree = tree
        self.passing_tests = passing_tests
        self.failing_tests = failing_tests
        self.k = k
        self.extra_templates = extra_templates
        self.log = log

        self.mutator = Mutator(self.old_tree, line_no, log)

    def repair(self) -> bool:
        """Entry point."""
        if self.log:
            print('Program to repair:')
            print(ast.unparse(self.old_tree))

        for template in self.mutator.apply():
            synthesizer = Synthesizer(template, self.passing_tests, self.failing_tests,
                                      k=self.k, extra_templates=self.extra_templates, log=self.log)
            if synthesizer.apply():
                self.new_tree = synthesizer.concrete_tree
                if self.log:
                    print('Program fixed:')
                    print(ast.unparse(self.new_tree))

                return True

        return False

    def validate(self, failures: List[str] = None) -> bool:
        """Check correctness of repaired program.
        Collect failure test case names in `failures` if provided."""
        return run_tests(self.new_tree, self.passing_tests + self.failing_tests, failures=failures)
