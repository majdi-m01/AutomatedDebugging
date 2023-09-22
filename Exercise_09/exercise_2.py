import ast
import copy
import random
from typing import Any, Callable, List, Set, Tuple, cast
from debuggingbook.StatisticalDebugger import OchiaiDebugger
from debuggingbook.Repairer import StatementMutator, Repairer

def comparator_mutation_candidates(node: ast.Compare) -> Set[ast.Compare]:
    candidates = set()
    if isinstance(node.ops[0], ast.Lt):
        candidates.add(ast.Compare(left=node.left, ops=[ast.LtE()], comparators=node.comparators))
        candidates.add(ast.Compare(left=node.left, ops=[ast.Gt()], comparators=node.comparators))
    elif isinstance(node.ops[0], ast.LtE):
        candidates.add(ast.Compare(left=node.left, ops=[ast.Lt()], comparators=node.comparators))
        candidates.add(ast.Compare(left=node.left, ops=[ast.GtE()], comparators=node.comparators))
    elif isinstance(node.ops[0], ast.Gt):
        candidates.add(ast.Compare(left=node.left, ops=[ast.GtE()], comparators=node.comparators))
        candidates.add(ast.Compare(left=node.left, ops=[ast.Lt()], comparators=node.comparators))
    elif isinstance(node.ops[0], ast.GtE):
        candidates.add(ast.Compare(left=node.left, ops=[ast.Gt()], comparators=node.comparators))
        candidates.add(ast.Compare(left=node.left, ops=[ast.LtE()], comparators=node.comparators))
    return candidates

def collect_atomic_conditions(tree: ast.AST) -> List[ast.expr]:
    pass

class ConditionGenerator:
    """Generate conditions built from the atomic conditions in an AST"""

    def __init__(self, tree: ast.AST) -> None:
        self.atomic_conditions = collect_atomic_conditions(tree)

    def sample(self) -> ast.expr:
        """Return a random condition."""
        pass

class ConditionMutator(StatementMutator):
    """Mutate conditions in an AST"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Constructor. Arguments are as with `StatementMutator` constructor."""
        super().__init__(*args, **kwargs)

    def mutate(self, tree: ast.AST) -> ast.AST:
        self.condition_generator = ConditionGenerator(tree)
        return super().mutate(tree)

    def choose_op(self) -> Callable:
        return self.swap # always do swapping

    def choose_bool_op(self) -> str:
        return random.choice(['set', 'not', 'and', 'or'])

    def swap(self, node: ast.AST) -> ast.AST:
        """Replace `node` condition by a constructed condition"""
        if not hasattr(node, 'test'):
            return node  # do not mutate nodes other than conditional statements

        node = cast(ast.If, node)
        new_node = copy.deepcopy(node)

        # TODO: YOUR CODE HERE

        return new_node

### TESTS ###

# (a)

def test_comparator_mutation_candidates(cond: str, expected: Set[str]):
    candidates = comparator_mutation_candidates(ast.parse(cond).body[0].value)
    actual = set([ast.unparse(e) for e in candidates])
    assert actual == expected

def test_a():
    test_comparator_mutation_candidates('x <= 10', set(['x < 10', 'x >= 10']))
    test_comparator_mutation_candidates('a + b > 0', set(['a + b >= 0', 'a + b < 0']))

# (b)

def should_sample(tree: ast.AST, expected: Set[str]):
    g = ConditionGenerator(tree)

    fuel = 10000
    while len(expected) > 0 and fuel >= 0:
        c = ast.unparse(g.sample())
        if c in expected:
            expected.remove(c)

        fuel -= 1

    if len(expected) > 0:
        raise AssertionError(f"expected conditions '{expected}' were not generated")

def a_loop(i: int, flag: bool):
    while i >= -5 and (i < 5 or i == 5):
        if i > 0 or flag:
            i = i - 1

def test_b():
    import inspect
    a_loop_tree = ast.parse(inspect.getsource(a_loop))
    should_sample(a_loop_tree, set([
        'i >= -5',
        'i <= 5',
        'i >= -5 and i <= 5',
        'i > 0 or not flag',
        'i > 0 and flag',
    ]))

# (c) first example

def sort_by_second_descending(lst: List[Tuple[str, int]]) -> List[Tuple[str, int]]:
    for i in range(0, len(lst) - 1):
        for j in range(i + 1, len(lst)):
            if lst[i][1] > lst[j][1]: # expect '<'
                tmp = lst[i]
                lst[i] = lst[j]
                lst[j] = tmp

    return lst

def sort_by_second_descending_test(inp: List[Tuple[str, int]], expected: List[Tuple[str, int]]):
    outp = sort_by_second_descending([(v, k) for v, k in inp]) 
    # copy because the input array will be written
    assert outp == expected

def test_c_1():
    PASSING_TESTS = [
        ([], []),
        ([('x', 3)], [('x', 3)]),
        ([('a', 10), ('b', 10)], [('a', 10), ('b', 10)]),
    ]

    FAILING_TESTS = [
        ([('a', 3), ('b', 10)], [('b', 10), ('a', 3)]),
        ([('A', 18), ('B', 23), ('A', 19), ('B', 30), ('B', 17)],
        [('B', 30), ('B', 23), ('A', 19), ('A', 18), ('B', 17)])
    ]

    for i in range(3):
        print('--> repairing sort_by_second_descending')
        debugger = OchiaiDebugger()
        for x, y in PASSING_TESTS + FAILING_TESTS:
            with debugger:
                sort_by_second_descending_test(x, y)
        repairer = Repairer(debugger, mutator_class=ConditionMutator)
        tree, fitness = repairer.repair()
        if fitness == 1.0:
            print('--> Found candidate with fitness=1.0 for sort_by_second_descending')
            break

# (c) second example

def multiple_2_3_5(n: int) -> bool:
    if n % 2 == 0:
        pass
    
    if n % 3 == 0:
        pass
    
    if n % 5 == 0:  # expected '(n % 2 == 0 and n % 3 == 0) and n % 5 == 0'
        return True
    else:
        return False

def multiple_2_3_5_test(n: int):
    assert multiple_2_3_5(n) == (n % 2 == 0 and n % 3 == 0 and n % 5 == 0)

def test_c_2():
    PASSING_TEST_INPUTS = [30, 60, 90, 2, 3, 6]
    FAILING_TEST_INPUTS = [5, 10, 15, 20, 40, 50]

    for i in range(3):
        print('--> repairing multiple_2_3_5_test')
        debugger = OchiaiDebugger()
        for n in PASSING_TEST_INPUTS + FAILING_TEST_INPUTS:
            with debugger:
                multiple_2_3_5_test(n)
        repairer = Repairer(debugger, mutator_class=ConditionMutator)
        tree, fitness = repairer.repair()
        if fitness == 1.0:
            print('--> Found candidate with fitness=1.0 for multiple_2_3_5_test')
            break

if __name__ == '__main__':
    test_a()
    test_b()
    test_c_1()
    test_c_2()
