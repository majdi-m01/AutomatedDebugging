import ast
from ast import FunctionDef, NodeTransformer, fix_missing_locations, parse, expr, stmt, unparse
import inspect
from typing import Any, Callable


######## Test examples ########


def fib(n: int) -> int:
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fib(n - 1) + fib(n - 2)


# https://www.geeksforgeeks.org/python-program-for-merge-sort/


def merge(arr, l, m, r):  # auxiliary function, do not trace
    n1 = m - l + 1
    n2 = r - m

    L = [0] * (n1)
    R = [0] * (n2)

    for i in range(0, n1):
        L[i] = arr[l + i]

    for j in range(0, n2):
        R[j] = arr[m + 1 + j]

    i = 0
    j = 0
    k = l

    while i < n1 and j < n2:
        if L[i] <= R[j]:
            arr[k] = L[i]
            i += 1
        else:
            arr[k] = R[j]
            j += 1
        k += 1

    while i < n1:
        arr[k] = L[i]
        i += 1
        k += 1

    while j < n2:
        arr[k] = R[j]
        j += 1
        k += 1


def merge_sort(arr, l, r):  # main function
    if l < r:
        m = l + (r - l) // 2

        merge_sort(arr, l, m)  # <--- trace this
        merge_sort(arr, m + 1, r)  # <--- trace this
        merge(arr, l, m, r)  # <--- do not trace this!

    return arr


#############

def parse_expr(code: str) -> expr:
    return parse(code, mode='eval').body


def parse_stmt(code: str) -> stmt:
    return parse(code, mode='exec').body[0]


def log(*objects: Any):
    print(*objects)


def returned(return_val: Any, level: int) -> Any:
    log('  ' * level + f"return {repr(return_val)}")
    return return_val


class Transformer(NodeTransformer):
    def visit_Return(self, node):
        self.generic_visit(node)
        returnNode = ast.Return(ast.Call(func=ast.Name(id="returned",
                                                       ctx=ast.Load()),
                                         args=[node.value,
                                               ast.Name(id="level",
                                                        ctx=ast.Load())],
                                         keywords=[]))
        ast.copy_location(node, returnNode)
        return returnNode

    def visit_Call(self, node):
        self.generic_visit(node)
        callNode = ast.Call(node.func,
                            node.args,
                            node.keywords)
        if self.ori_name == node.func.id and isinstance(node.func, ast.Name):
            callNode.func.id = self.traced_name
            callNode.args.append(ast.BinOp(left=ast.Name(id="level",
                                                         ctx=ast.Load()),
                                           op=ast.Add(),
                                           right=ast.Num(n=1)))
        ast.copy_location(node, callNode)
        return callNode

    def visit_FunctionDef(self, node: FunctionDef) -> FunctionDef:
        self.ori_name = node.name
        self.traced_name = node.name + '_traced'

        self.generic_visit(node)
        newNode = FunctionDef(self.traced_name,
                              node.args,
                              node.body,
                              node.decorator_list,
                              node.returns,
                              node.type_comment)

        level_Arg = ast.AnnAssign(target=ast.Name(id='level', ctx=ast.Store()),
                                  annotation=ast.Name(id='int', ctx=ast.Load()),
                                  value=ast.Name(id='0', ctx=ast.Load()),
                                  simple=1)
        newNode.args.args.append(level_Arg)

        if node.name == 'fib':
            log_call = ast.Expr(value=ast.Call(func=ast.Name(id="log", ctx=ast.Load()),
                                               args=[ast.BinOp(
                                                   left=ast.BinOp(
                                                       left=ast.Str(s=' '),
                                                       op=ast.Mult(),
                                                       right=ast.Name(
                                                           id="level",
                                                           ctx=ast.Load())
                                                   ),
                                                   op=ast.Add(),
                                                   right=ast.JoinedStr(values=[
                                                       ast.Str(s='call with n = '),
                                                       ast.FormattedValue(value=ast.Name(id='n', ctx=ast.Load()),
                                                                          conversion=-1, format_spec=None)
                                                   ]))
                                               ],
                                               keywords=[]))
        if node.name == 'merge_sort':
            log_call = ast.Expr(value=ast.Call(func=ast.Name(id="log", ctx=ast.Load()),
                                               args=[ast.BinOp(
                                                   left=ast.BinOp(
                                                       left=ast.Str(s=' '),
                                                       op=ast.Mult(),
                                                       right=ast.Name(
                                                           id="level",
                                                           ctx=ast.Load())
                                                   ),
                                                   op=ast.Add(),
                                                   right=ast.JoinedStr(values=[
                                                       ast.Str(s='call with arr = '),
                                                       ast.FormattedValue(value=ast.Name(id='arr', ctx=ast.Load()),
                                                                          conversion=-1, format_spec=None),
                                                       ast.Str(s=', l = '),
                                                       ast.FormattedValue(value=ast.Name(id='l', ctx=ast.Load()),
                                                                          conversion=-1, format_spec=None),
                                                       ast.Str(s=', r = '),
                                                       ast.FormattedValue(value=ast.Name(id='r', ctx=ast.Load()),
                                                                          conversion=-1, format_spec=None),
                                                   ]))
                                               ],
                                               keywords=[]))
        newNode.body.insert(0, log_call)

        ast.copy_location(node, newNode)
        return newNode


######## Tests ########

def call_traced(original_func: Callable, *args: Any) -> None:
    original_ast = parse(inspect.getsource(original_func))
    tr = Transformer()
    new_ast = tr.visit(original_ast)
    assert isinstance(new_ast.body[0], FunctionDef)

    new_func_code = unparse(fix_missing_locations(new_ast.body[0]))
    call_args = [repr(x) for x in args]
    call_func_code = f"{tr.traced_name}({', '.join(call_args)})"
    # to avoid scope issues, we simply wrap up the recursive func def and call in a closure
    code = f"def go():\n{with_indent(new_func_code)}\n{with_indent(call_func_code)}\ngo()"

    # Uncomment the following to show the final code
    from debuggingbook.bookutils import print_content
    print_content(code, '.py')
    print()

    exec(code)


def with_indent(code: str, level=1) -> str:
    lines = code.split('\n')
    indented = ['    ' * level + line for line in lines]
    return '\n'.join(indented)


if __name__ == '__main__':
    call_traced(fib, 4)

    arr = [12, 11, 13, 5, 6, 7]
    call_traced(merge_sort, arr, 0, len(arr) - 1)
