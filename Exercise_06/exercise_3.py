import ast
from typing import Any, Optional, Dict, List, Tuple
from ast import NodeVisitor

############## TYPES ##############

class Type:
    def __eq__(self, other):
        return isinstance(other, Anything) or type(self) == type(other)

    def __repr__(self) -> str:
        return self.__class__.__name__
    
    def __str__(self) -> str:
        return self.__repr__()
    

class Anything(Type):
    def __eq__(self, other):
        return isinstance(other, Type)
    

class Int(Type):
    pass


class Str(Type):
    pass

############# SCOPES ##############

class TypeScope:
    
    def __init__(self, parent=None):
        self.parent = parent
        self.types: Dict[str, Type] = dict()
        
    def enter(self) -> Any:
        return TypeScope(self)
    
    def exit(self) -> Any:
        return self.parent if self.parent else self
    
    def put(self, name: str, type_: Type) -> None:
        self.types[name] = type_
        
    
    def get(self, name: str) -> Optional[Type]:
        if name in self.types:
            return self.types[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            return None
        
    def update(self, name: str, type_: Type):
        if name in self.types:
            self.types[name] = type_
            return True
        elif self.parent:
            result = self.parent.update(name, type_)
            if not result:
                self.put(name, type_)
        return False
    

class FunctionScope:
    
    def __init__(self):
        self.types: Dict[str, Tuple[List[Type], Type]] = dict()
    
    def put(self, name: str, types: Tuple[List[Type], Type]) -> None:
        self.types[name] = types
        
    
    def get(self, name: str) -> Optional[Tuple[List[Type], Type]]:
        if name in self.types:
            return self.types[name]
        else:
            return None
        
########## TYPE CHECKING ##########

class ForwardTypeChecker(ast.NodeVisitor):
    
    def __init__(self):
        self.scope = TypeScope()
        self.functions = FunctionScope()
        self.current_return = None
        
    def generic_visit(self, node: ast.AST) -> Optional[Type]:
        raise SyntaxError(f'Unsupported node {node.__class__.__name__}')
        
    def visit_Module(self, node: ast.Module) -> Optional[Type]:
        for n in node.body:
            self.visit(n)
        return None
        
    def visit_FunctionDef(self, node: ast.FunctionDef) -> Optional[Type]:
        assert self.current_return is None, \
            f'Nested function {node.name}'
        self.scope = self.scope.enter()
        types = list()

        # TODO: iterate over args, add the types (arg.annotation) in order of
        # TODO: appearance to the types variable, and put the types in the scope.

        for arg in node.args.args:
            types.append((arg.arg, ast.unparse(arg.annotation)))

        for tuple in types:
            if tuple[1]=='int':
                self.scope.update(tuple[0], Int())
            elif tuple[1]=='str':
                self.scope.update(tuple[0], Str())
            else:
                self.scope.update(tuple[0], Anything())

        returns = Anything()
        
        # TODO: find the correct value for returns that matches the function return value
        if node.returns is not None:
            if ast.unparse(node.returns) == 'int':
                returns = Int()
            elif ast.unparse(node.returns) == 'str':
                returns = Str()
            else:
                returns = Anything()
        else:
            returns = Anything()

        self.functions.put(node.name, (types, returns))
        self.current_return = returns
        
        # TODO: iterate over node.body to perform a type check of the body
        self.visit_Module(node)

        self.current_return = None
        self.scope = self.scope.exit()
        return None
    
    def visit_Assign(self, node: ast.Assign) -> Optional[Type]:
        assert len(node.targets) == 1, \
            'Targets is longer than 1'
        assert isinstance(node.targets[0], ast.Name), \
            'Target is not a Name'
        target = node.targets[0]

        # TODO: find the type of the assigned expression and update the target's (target.id) type in self.scope
        target_type = self.visit_Name(target)
        self.scope.types.update(target.id, target_type)
        return None
    
    def visit_AnnAssign(self, node: ast.AnnAssign) -> Optional[Type]:
        assert isinstance(node.target, ast.Name), \
            'Target is not a Name'
        assert isinstance(node.annotation, ast.Name), \
            'Annotation is not a Name'
        assert node.value is not None, \
            'Value is None'

        # TODO: find the type of the assigned expression and the type of the target (hint: node.annotation)
        # TODO: and check if they match
        if isinstance(node.value, ast.Call):
            type_call = self.visit_Call(node.value)
        if type_call.__repr__().lower() == ast.unparse(node.annotation):
            self.scope.update(node.target.id, type_call)
        else:
            raise TypeError
        return None
    
    def visit_Expr(self, node: ast.Expr) -> Optional[Type]:
        # TODO: check the type of the expression
        if isinstance(node.value, ast.Name):
            type_value = self.visit_Name(node.value)
        elif isinstance(node.value, ast.BinOp):
            type_value = self.visit_BinOp(node.value)
        if type(type_value).__name__ == 'Int':
            return Int()
        elif type(type_value).__name__ == 'Str':
            return Str()
        else:
            return Anything()
    
    def visit_Return(self, node: ast.Return) -> Optional[Type]:
        # TODO: get the type of the return value and compare it to the current_return type
        if isinstance(node.value, ast.BinOp):
            type_value = self.visit_BinOp(node.value)
        elif isinstance(node.value, ast.Name):
            type_value = self.visit_Name(node.value)

        if type_value.__repr__() == 'Int' and (type(self.current_return).__name__ == 'Int' or type(self.current_return).__name__ == 'Anything'):
            return Int()
        elif type_value.__repr__() == 'Str' and (type(self.current_return).__name__ == 'Str' or type(self.current_return).__name__ == 'Anything'):
            return Str()
        elif type_value.__repr__() == 'Anything' and type(self.current_return).__name__ == 'Anything':
            return Anything()
        else:
            raise TypeError

    def visit_Name(self, node: ast.Name) -> Optional[Type]:
        # TODO: get the type of the node (node.id) and raise a TypeError
        # TODO: if it does not exist, Return the type of the expression
        if not self.scope.types.get(node.id):
            raise TypeError
        else:
            if self.scope.types.get(node.id).__repr__() == 'Int':
                return Int()
            elif self.scope.types.get(node.id).__repr__() == 'Str':
                return Str()
            elif self.scope.types.get(node.id).__repr__() == 'Anything':
                return Anything()

    def visit_BinOp(self, node: ast.BinOp) -> Optional[Type]:
        assert (isinstance(node.op, ast.Add) or
                isinstance(node.op, ast.Mult)), \
            f'Unsupported op {node.op.__class__.__name__}'

        # TODO: get the types of left and right, check that they match with the operator Add (+) or Mult (*)
        # TODO: Return the type of the expression
        if isinstance(node.left, ast.Name):
            type_left = self.visit_Name(node.left)
        elif isinstance(node.left, ast.Constant):
            type_left = self.visit_Constant(node.left)
        if isinstance(node.right, ast.Name):
            type_right = self.visit_Name(node.right)
        elif isinstance(node.right, ast.Constant):
            type_right = self.visit_Constant(node.right)
        name_type_left = type(type_left).__name__
        name_type_right = type(type_right).__name__

        if isinstance(node.op, ast.Add):
            if name_type_left == 'Int' and name_type_right == 'Int':
                return Int()
            elif name_type_left == 'Int' and name_type_right == 'Str':
                raise TypeError
            elif name_type_left == 'Int' and name_type_right == 'Anything':
                return Int()
            elif name_type_left == 'Str' and name_type_right == 'Int':
                raise TypeError
            elif name_type_left == 'Str' and name_type_right == 'Str':
                return Str()
            elif name_type_left == 'Str' and name_type_right == 'Anything':
                return Str()
            elif name_type_left == 'Anything' and name_type_right == 'Int':
                return Int()
            elif name_type_left == 'Anything' and name_type_right == 'Str':
                return Str()
            elif name_type_left == 'Anything' and name_type_right == 'Anything':
                return Anything()
        elif isinstance(node.op, ast.Mult):
            if name_type_left == 'Int' and name_type_right == 'Int':
                return Int()
            elif name_type_left == 'Int' and name_type_right == 'Str':
                return Str()
            elif name_type_left == 'Int' and name_type_right == 'Anything':
                return Int()
            elif name_type_left == 'Str' and name_type_right == 'Int':
                return Str()
            elif name_type_left == 'Str' and name_type_right == 'Str':
                raise TypeError
            elif name_type_left == 'Str' and name_type_right == 'Anything':
                return Str()
            elif name_type_left == 'Anything' and name_type_right == 'Int':
                return Int()
            elif name_type_left == 'Anything' and name_type_right == 'Str':
                return Str()
            elif name_type_left == 'Anything' and name_type_right == 'Anything':
                return Anything()


    def visit_Call(self, node: ast.Call) -> Optional[Type]:
        assert isinstance(node.func, ast.Name), \
            'Func is not a Name'
        expected_types = self.functions.get(node.func.id)
        assert expected_types is not None, \
            'Func not defined'
        expected_types, return_type = expected_types
        assert len(expected_types) == len(node.args), \
            'Number of args do not match'
        # TODO: check that the expected types match with the given arguments
        for i, j in zip(expected_types, node.args):
            if isinstance(j, ast.Constant):
                j_type = self.visit_Constant(j)
            if j_type.__repr__().lower() == i[1]:
                if j_type.__repr__() == 'Int' and i[1] == 'int' and (return_type.__repr__() == 'Int' or return_type.__repr__() == 'Anything'):
                    return_type = Int()
                elif j_type.__repr__() == 'Str' and i[1] == 'str' and (return_type.__repr__() == 'Str' or return_type.__repr__() == 'Anything'):
                    return_type = Str()
            else:
                raise TypeError
        return return_type
    
    def visit_Constant(self, node: ast.Constant) -> Optional[Type]:
        # TODO: check the type of the value and return our Type format that matches
        if isinstance(node.value, int):
            return Int()
        elif isinstance(node.value, str):
            return Str()
        else:
            return Anything()
    

############## TESTS ##############

def test(program: str, failing: bool = False):
    try:
        tree = ast.parse(program)
        checker = ForwardTypeChecker()
        checker.visit(tree)
    except AssertionError:
        pass
    except SyntaxError:
        pass
    except TypeError:
        return failing
    else:
        return not failing
    

if __name__ == '__main__':
    assert test('''
def f(x: int, y: int) -> int:
    return x + y

z: int = f(2, 3)
'''), 'test 1 failed'

    assert test('''
'a' + 3
''', failing=True), 'test 2 failed'

    assert test('''
def f(x: int) -> str:
    return x
''', failing=True), 'test 3 failed'

    assert test('''
a
''', failing=True), 'test 4 failed'
    assert test('''
def f(x: int):
    return x

y: int = f(2)
'''), 'test 5 failed'

    assert test('''
def f(x: int) -> str:
    return 'a' * x

y: int = f(2)
''', failing=True), 'test 6 failed'

    assert test('''
def f(x: int) -> int:
    return x

y: int = f('a')
''', failing=True), 'test 7 failed'
#