from debuggingbook.Slicer import Slicer
from typing import Any, Dict, Set, Tuple
import inspect
import ast

############## BUG FIX ##############

from debuggingbook.Slicer import DependencyTracker
_data = DependencyTracker()

############## REDUCER ##############
class Reducer(ast.NodeTransformer):
    
    def __init__(self, lines: Set[int]):
        self.lines = lines
        
    def generic_visit(self, node: ast.AST):
        if hasattr(node, 'lineno') and node.lineno not in self.lines:
            return None
        for field, old_value in ast.iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, ast.AST):
                        value = self.visit(value)
                        if value is None:
                            continue
                        elif not isinstance(value, ast.AST):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, ast.AST):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        if hasattr(node, 'body'):
            if not node.body and all(map(lambda x: x is None, node.body)):
                node.body = [
                    ast.Pass(),
                ]
        return node
#####################################

def middle(x, y, z):  # type: ignore
    if y < z:
        if x < y:
            return y
        elif x < z:
            return y
    else:
        if x > y:
            return y
        elif x > z:
            return x
    return z

class ReduceSlicer(Slicer):
    
    def reduce(self, sources: Dict[str, Tuple[str, int]]) -> str:
        result = ''
        # TODO: implement this method

        # Extract starting line number and the source code
        for key, value in sources.items():
            starting_line: int = value[1]
            source_code: str = value[0]

        # Create a set and extract unique used lines from data and control dependencies into the set
        used_lines = set()
        for key, value in self.dependencies().control:
            used_lines.add(value[1])
        for key, value in self.dependencies().data:
            used_lines.add(value[1])

        # Renumber the lines from 1
        used_lines = [line - starting_line + 1 for line in used_lines]

        # Produce a tree and visit the corresponding used lines
        reducer = Reducer(used_lines)
        tree = ast.parse(source_code)
        new_tree = reducer.visit(tree)

        # Unparse Result
        result += ast.unparse(new_tree)

        return result
    
if __name__ == '__main__':
    with ReduceSlicer(middle) as rs:
        m = middle(2, 1, 3)
    m_test = middle(1, 3, 2)
    _, start = inspect.getsourcelines(middle)
    f = rs.reduce({middle.__name__: (inspect.getsource(middle), start)})
    print(f)
    assert f == """def middle(x, y, z):
    if y < z:
        if x < y:
            pass
        elif x < z:
            return y"""
    exec(f)
    m2 = middle(2, 1, 3)
    assert m == m2, f'expected {m}, but was {m2} on slice'
    m3 = middle(1, 3, 2)
    assert m_test != m3 and m3 is None, f'expected {m_test}, but was {m3} not on slice'
