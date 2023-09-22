from abc import abstractmethod
import ast
import inspect
import unittest
from typing import List, Optional
from textwrap import dedent
from repair.mutator import *

### Tests for Marker ###

class LineLocator(ast.NodeVisitor):
    def __init__(self, line_no: int) -> None:
        super().__init__()

        self.line_no = line_no
        self.target: ast.stmt
    
    def generic_visit(self, node: ast.AST) -> None:
        if isinstance(node, ast.stmt) and node.lineno == self.line_no:
            self.target = node
            return

        super().generic_visit(node)

class TestMarker(object): # mixin class
    source: str
    line_no: int
    in_loop_body: bool
    is_first_stmt: bool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        cls.tree = ast.parse(dedent(cls.source))
        locator = LineLocator(cls.line_no)
        locator.visit(cls.tree)
        cls.target = locator.target

        cls.marker = Marker(cls.line_no)
        cls.marker.visit(cls.tree)

    def test_mark(self):
        self.assertTrue(self.marker.found)
        self.assertTrue(hasattr(self.target, '__target__'))

    def test_mark_in_loop_body(self):
        self.assertEqual(self.target.__target__[0], self.in_loop_body)

    def test_mark_is_first_stmt(self):
        self.assertEqual(self.target.__target__[1], self.is_first_stmt)

class TestMarkerSimple(TestMarker, unittest.TestCase):
    source = """\
        def foo():
            x = 1
    """
    line_no = 2
    in_loop_body = False
    is_first_stmt = True

class TestMarkerIf(TestMarker, unittest.TestCase):
    source = """\
        def foo():
            if True:
                x = 1
                x += 1
    """
    line_no = 4
    in_loop_body = False
    is_first_stmt = False

class TestMarkerWhile(TestMarker, unittest.TestCase):
    source = """\
        def foo():
            while True:
                x = 1
                x += 1
    """
    line_no = 3
    in_loop_body = True
    is_first_stmt = True

class TargetLocator(ast.NodeVisitor):
    def __init__(self) -> None:
        super().__init__()

        self.found = False
    
    def generic_visit(self, node: ast.AST) -> None:
        if hasattr(node, '__target__'):
            self.found = True
            return

        super().generic_visit(node)

class TestMarkerNoMark(unittest.TestCase):
    def test_no_mark(self):
        self.tree = ast.parse(dedent("""\
            def foo():
                x = 1
        """))
        marker = Marker(3)
        marker.visit(self.tree)
        self.assertFalse(marker.found)

        locator = TargetLocator()
        locator.visit(self.tree)
        self.assertFalse(locator.found)

### Tests for MutationOperator ###

class TestMutationOperator(unittest.TestCase):
    def get_op(self) -> MutationOperator:
        pass

    def assert_trans(self, old_source: str, line_no: int, new_source: Optional[str]) -> None:
        source = dedent(old_source)
        expected = dedent(new_source).strip() if new_source else None
        mutator = Mutator(ast.parse(source), line_no)
        actual = [ast.unparse(tree) for tree in mutator.apply([self.get_op()])]

        if expected is None:
            if actual == []:
                pass
            else:
                self.assertTrue(len(actual) == 1)
                actual = actual[0]
                raise self.failureException('this transformation should be not applied, '
                                            f'but found\n{actual}')
        else:
            if actual == []:
                raise self.failureException(f'expect\n{expected}\n'
                                            f'but the transformation did not apply')
            else:
                self.assertTrue(len(actual) == 1)
                actual = actual[0]
                self.assertEqual(actual, expected, f'expect\n{expected}\nbut found\n{actual}')

class TestTighten(TestMutationOperator):
    def get_op(self) -> MutationOperator:
        return Tighten()

    def test_tighten_if_cond(self):
        self.assert_trans("""\
            def foo():
                if True:
                    pass
        """, 2, """\
            def foo():
                if True and (not __abstract__):
                    pass
        """)

    def test_tighten_if_cond_inside_loop(self):
        self.assert_trans("""\
            def foo():
                while True:
                    if True:
                        pass
        """, 3, """\
            def foo():
                while True:
                    if True and (not __abstract__):
                        pass
        """)

    def test_tighten_nested_if_cond(self):
        self.assert_trans("""\
            def foo():
                if True:
                    if True:
                        pass
        """, 3, """\
            def foo():
                if True:
                    if True and (not __abstract__):
                        pass
        """)

    def test_tighten_elif_cond(self):
        self.assert_trans("""\
            def foo():
                if False:
                    pass
                elif True and True:
                    pass
        """, 4, """\
            def foo():
                if False:
                    pass
                elif (True and True) and (not __abstract__):
                    pass
        """)

    def test_tighten_non_if_cond(self):
        self.assert_trans("""\
            def foo():
                if False:
                    pass
                x = 0
        """, 4, None)

class TestLoosen(TestMutationOperator):
    def get_op(self) -> MutationOperator:
        return Loosen()

    def test_loosen_if_cond(self):
        self.assert_trans("""\
            def foo():
                if True:
                    pass
        """, 2, """\
            def foo():
                if True or __abstract__:
                    pass
        """)

    def test_loosen_if_cond_inside_loop(self):
        self.assert_trans("""\
            def foo():
                while True:
                    if True:
                        pass
        """, 3, """\
            def foo():
                while True:
                    if True or __abstract__:
                        pass
        """)

    def test_loosen_nested_if_cond(self):
        self.assert_trans("""\
            def foo():
                if True:
                    if True:
                        pass
        """, 3, """\
            def foo():
                if True:
                    if True or __abstract__:
                        pass
        """)

    def test_loosen_elif_cond(self):
        self.assert_trans("""\
            def foo():
                if False:
                    pass
                elif True and True:
                    pass
        """, 4, """\
            def foo():
                if False:
                    pass
                elif True and True or __abstract__:
                    pass
        """)

    def test_loosen_non_if_cond(self):
        self.assert_trans("""\
            def foo():
                if False:
                    pass
                x = 0
        """, 4, None)

class TestGuard(TestMutationOperator):
    def get_op(self) -> MutationOperator:
        return Guard()

    def test_guard_stmt(self):
        self.assert_trans("""\
            def foo():
                if True:
                    y = x
        """, 3, """\
            def foo():
                if True:
                    if not __abstract__:
                        y = x
        """)
    
    def test_guard_nested_stmt(self):
        self.assert_trans("""\
            def foo():
                x = 0
                if x == 0:
                    y = x
        """, 4, """\
            def foo():
                x = 0
                if x == 0:
                    if not __abstract__:
                        y = x
        """)

class TestBreakFirst(TestMutationOperator):
    def get_op(self) -> MutationOperator:
        return Break(True)
    
    def test_break_first_while(self):
        self.assert_trans("""\
            def foo():
                i = 0
                while True:
                    i += 1
        """, 4, """\
            def foo():
                i = 0
                while True:
                    if __abstract__:
                        break
                    i += 1
        """)

    def test_break_first_for(self):
        self.assert_trans("""\
            def foo(xs):
                y = 0
                for x in xs:
                    y += x
        """, 4, """\
            def foo(xs):
                y = 0
                for x in xs:
                    if __abstract__:
                        break
                    y += x
        """)

    def test_break_first_outside_loop(self):
        self.assert_trans("""\
            def foo(xs):
                if True:
                    x = xs[0]
        """, 3, None)

    def test_break_first_given_second(self):
        self.assert_trans("""\
            def foo():
                i = 0
                while True:
                    pass
                    i += 1
        """, 5, None)

class TestBreakRest(TestMutationOperator):
    def get_op(self) -> MutationOperator:
        return Break(False)
    
    def test_break_rest_while(self):
        self.assert_trans("""\
            def foo():
                i = 0
                while True:
                    pass
                    i += 1
        """, 5, """\
            def foo():
                i = 0
                while True:
                    pass
                    if __abstract__:
                        break
                    i += 1
        """)

    def test_break_rest_for(self):
        self.assert_trans("""\
            def foo(xs):
                y = 0
                for x in xs:
                    pass
                    y += x
        """, 5, """\
            def foo(xs):
                y = 0
                for x in xs:
                    pass
                    if __abstract__:
                        break
                    y += x
        """)

    def test_break_rest_outside_loop(self):
        self.assert_trans("""\
            def foo(xs):
                while False:
                    pass
                else:
                    x = xs[0]
        """, 5, None)

    def test_break_rest_given_first(self):
        self.assert_trans("""\
            def foo():
                i = 0
                while True:
                    i += 1
                    pass
        """, 4, None)

### Tests for Mutator ###

class TestMutator(unittest.TestCase):
    source: str
    line_no: int

    @classmethod
    def setUpClass(cls):
        mutator = Mutator(ast.parse(dedent(cls.source)), cls.line_no)
        cls.results = [ast.unparse(t).splitlines() for t in mutator.apply()]

    def assert_contains_line(self, expected: str, line_no: int):
        for lines in self.results:
            if line_no <= len(lines) and lines[line_no - 1].strip() == expected:
                return

        raise self.failureException('cannot find expected source line:\n'
                                    f'{line_no}  {expected}')


class TestMutatorSimple(TestMutator):
    source = """\
        def foo(x):
            x += 1
    """
    line_no = 2

    def test_mutate_simple_mutants_count(self):
        self.assertEqual(len(self.results), 1)

    def test_mutate_simple_index_guard(self):
        self.assert_contains_line('if not __abstract__:', 2)

class TestMutatorWhile(TestMutator):
    source = """\
        def foo(x):
            if x > 0:
                pass
            else:
                while True:
                    x += 1
    """
    line_no = 6

    def test_mutate_while_mutants_count(self):
        self.assertEqual(len(self.results), 2)

    def test_mutate_while_guard(self):
        self.assert_contains_line('if not __abstract__:', 6)

    def test_mutate_while_break(self):
        self.assert_contains_line('break', 7)

class TestMutatorCharIndex(TestMutator):
    from repair.benchmarks import char_index
    source = inspect.getsource(char_index)
    line_no = 9

    def test_mutate_char_index_mutants_count(self):
        self.assertEqual(len(self.results), 4)

    def test_mutate_char_index_tighten(self):
        self.assert_contains_line('if x == c and (not __abstract__):', 9)

    def test_mutate_char_index_loosen(self):
        self.assert_contains_line('if x == c or __abstract__:', 9)

    def test_mutate_char_index_guard(self):
        self.assert_contains_line('if not __abstract__:', 9)

    def test_mutate_char_index_break(self):
        self.assert_contains_line('break', 10)
