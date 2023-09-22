import ast
from typing import List


def compile_and_test_ast(tree: ast.Module, keep_list: List[ast.AST], 
                         test_tree: ast.FunctionDef) -> None:
    new_tree = cast(ast.Module, copy_and_reduce(tree, keep_list))
    if test_tree is not None:
        new_tree.body += test_tree.body
    try:
        code_object = compile(new_tree, '<string>', 'exec')
    except Exception:
        raise SyntaxError("Cannot compile")
    test_failed = False
    try:
        exec(code_object, {}, {})
    except AssertionError:
        test_failed = True
    if not test_failed:
        raise Exception

## TEST ##

def fib(n: int) -> int:
    if n == 0 or n == 1:
        return 1
    return fib(n - 1) + fib(n - 2)

def fib_test_simple():
    assert fib(0) == 1
    assert fib(1) == 1
    # assert fib(4) == 5

if __name__ == '__main__':
    fib_test_simple()

    import inspect
    from debuggingbook.DeltaDebugger import NodeCollector, DeltaDebugger, copy_and_reduce
    from debuggingbook.bookutils import print_content

    fun_tree: ast.Module = ast.parse(inspect.getsource(fib))
    fun_nodes = NodeCollector().collect(fun_tree)
    test_tree: ast.Module = ast.parse(inspect.getsource(fib_test_simple)).body[0]

    with DeltaDebugger() as dd:
        compile_and_test_ast(fun_tree, fun_nodes, test_tree)

    reduced_nodes = dd.min_args()['keep_list']
    reduced_fun_tree = copy_and_reduce(fun_tree, reduced_nodes)
    print_content(ast.unparse(reduced_fun_tree), '.py')