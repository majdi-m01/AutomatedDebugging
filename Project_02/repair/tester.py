import ast
import copy
from types import CodeType
from typing import Any, Iterator, List, Tuple

Env: type = dict[str, Any]

class Record:
    """Execution record.
    The actual values and local envs for each evaluation of the abstract condition."""
    def __init__(self, values: List[bool], envs: List[Env]):
        self.values = values
        self.envs = envs

    def __add__(self, other):
        return Record(self.values + other.values, self.envs + other.envs)

    def __repr__(self) -> str:
        s = ''
        for v, env in zip(self.values, self.envs):
            s += '__abstract__ = '
            s += 'True ' if v else 'False'
            s += f' under env {env}\n'
        return s

class Context:
    """Execution context.
    Obtain values for the abstract condition and maintain records."""
    def __init__(self, future_values: Iterator[bool]):
        self.future_values = future_values
        self.record = Record([], [])

    def next_value(self, env: Env) -> bool:
        value = next(self.future_values, False)
        self.record.values.append(value)
        self.record.envs.append(copy.deepcopy(env))
        return value

def mk_expr(code: str) -> ast.expr:
    stmt = ast.parse(code).body[0]
    assert isinstance(stmt, ast.Expr)
    return stmt.value

THE_CONTEXT_OBJECT = '__context__'

class Instantiate(ast.NodeTransformer):
    """Transform the abstract condition of an AST into a given expression `instantiation`."""
    def __init__(self, instantiation: ast.expr) -> None:
        super().__init__()

        assert isinstance(instantiation, ast.expr)
        self.instantiation = instantiation

    def visit_Name(self, node: ast.Name) -> ast.expr:
        if node.id == '__abstract__':
            return self.instantiation

        return node
    
def exec_abstract(tree: ast.Module, test_code: CodeType,
                  future_values: Iterator[bool]) -> Tuple[bool, Record]:
    """Run the `test` on a `tree` that involves an abstract condition,
    consuming condition values from `future_values`.
    Return if the test succeeds together with the execution record."""
    assert test_code.co_argcount == 0
    
    tree = copy.deepcopy(tree)
    the_expr = mk_expr(f'{THE_CONTEXT_OBJECT}.next_value(locals())')
    tree = Instantiate(the_expr).visit(tree)
    program_code = ast.unparse(tree)

    ctx = Context(future_values)
    env = { THE_CONTEXT_OBJECT : ctx }
    try:
        exec(program_code, env)
        exec(test_code, env)
    except Exception:
        success = False
    else:
        success = True

    return success, ctx.record

def all_true() -> Iterator[bool]:
    """Infinite stream of `True`s."""
    while True:
        yield True

def run_tests(tree: ast.Module, tests: List[CodeType], failures: List[str] = None) -> bool:
    """Check if `tree` is correct w.r.t. the tests.
    Collect failure test case names in `failures` if provided."""
    program_code = ast.unparse(tree)

    env = {}
    exec(program_code, env)
    passed = True

    for test_code in tests:
        try:
            exec(test_code, env)
        except Exception:
            passed = False
            if failures is not None and isinstance(failures, list):
                failures.append(test_code.co_name)

    return passed
