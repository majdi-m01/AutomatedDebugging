import os
import inspect

PRINT_FORMAT = '{:<50}{}'
CORRECT_STATE = 'OK'
WRONG_STATE = 'NOT OK'

files_to_verify = [
    os.path.join('verify.py'),
    os.path.join('exercise_1.py'),
    os.path.join('exercise_2a.py'),
    os.path.join('exercise_2b.py'),
    os.path.join('exercise_3.py'),
    # path to file
]

variables_to_verify = [
    ('exercise_1', 'data'),
    
    ('exercise_3', 'Type'),
    ('exercise_3', 'Anything'),
    ('exercise_3', 'Int'),
    ('exercise_3', 'Str'),
    ('exercise_3', 'TypeScope'),
    ('exercise_3', 'FunctionScope'),
    ('exercise_3', 'ForwardTypeChecker'),
    # tuple of (package, var name)
]

functions_to_verify = [
    # tuple of (package, function name, number of args)
    ('exercise_1', 'store_data', 1),
    ('exercise_1', 'get_data', 1),
    ('exercise_1', 'heartbeat', 2),
    
    ('exercise_2a', 'mystery', 2),
    ('exercise_2a', 'test_mystery', 0),
    ('exercise_2a', 'run', 0),
    
    ('exercise_2b', 'mystery', 2),
    ('exercise_2b', 'test_mystery', 0),
    ('exercise_2b', 'run', 0),
    
    ('exercise_3', 'Type.__eq__', 2),
    ('exercise_3', 'Type.__repr__', 1),
    ('exercise_3', 'Type.__str__', 1),
    ('exercise_3', 'Anything.__eq__', 2),
    
    ('exercise_3', 'TypeScope.__init__', 2),
    ('exercise_3', 'TypeScope.enter', 1),
    ('exercise_3', 'TypeScope.exit', 1),
    ('exercise_3', 'TypeScope.put', 3),
    ('exercise_3', 'TypeScope.get', 2),
    ('exercise_3', 'TypeScope.update', 3),
    
    ('exercise_3', 'FunctionScope.__init__', 1),
    ('exercise_3', 'FunctionScope.put', 3),
    ('exercise_3', 'FunctionScope.get', 2),
    
    ('exercise_3', 'ForwardTypeChecker.__init__', 1),
    ('exercise_3', 'ForwardTypeChecker.generic_visit', 2),
    ('exercise_3', 'ForwardTypeChecker.visit_Module', 2),
    ('exercise_3', 'ForwardTypeChecker.visit_FunctionDef', 2),
    ('exercise_3', 'ForwardTypeChecker.visit_Assign', 2),
    ('exercise_3', 'ForwardTypeChecker.visit_AnnAssign', 2),
    ('exercise_3', 'ForwardTypeChecker.visit_Expr', 2),
    ('exercise_3', 'ForwardTypeChecker.visit_Return', 2),
    ('exercise_3', 'ForwardTypeChecker.visit_Name', 2),
    ('exercise_3', 'ForwardTypeChecker.visit_BinOp', 2),
    ('exercise_3', 'ForwardTypeChecker.visit_Call', 2),
    ('exercise_3', 'ForwardTypeChecker.visit_Constant', 2),
]

def verify_files():
    missing_files = list()
    for path in files_to_verify:
        if os.path.exists(path):
            state = CORRECT_STATE
        else:
            missing_files.append(path)
            state = WRONG_STATE
        print(PRINT_FORMAT.format(path, state))
    print()
    return missing_files

def verify_variables():
    missing_variables = list()
    current_package = None
    for package, variable in variables_to_verify:
        if current_package is None or current_package.__name__ != package:
            current_package = __import__(package)
        varaible_repr = f'{package}.{variable}'
        if variable in dir(current_package):
            state = CORRECT_STATE
        else:
            missing_variables.append(varaible_repr)
            state = WRONG_STATE
        print(PRINT_FORMAT.format(varaible_repr, state))
    print()
    return missing_variables

def verify_functions():
    missing_functions = list()
    wrong_functions = list()
    current_package = None
    for package, function, args in functions_to_verify:
        if current_package is None or current_package.__name__ != package:
            current_package = __import__(package)
        fs = function.split('.')
        function_repr = f'{package}.{function}'
        if fs[0] in dir(current_package):
            f = getattr(current_package, fs[0])
            for i in fs[1:]:
                f = getattr(f, i)
            while hasattr(f, '__wrapped__'):
                f = f.__wrapped__
            specs = inspect.getfullargspec(f)
            if len(specs[0]) == args:
                state = CORRECT_STATE
            else:
                wrong_functions.append(function_repr)
                state = WRONG_STATE
        else:
            missing_functions.append(function_repr)
            state = WRONG_STATE
        print(PRINT_FORMAT.format(function_repr, state))
    print()
    return missing_functions, wrong_functions

class VerificationError(ValueError):
    pass

if __name__ == '__main__':
    missing_files = verify_files()
    missing_variables = verify_variables()
    missing_functions, wrong_functions = verify_functions()
    for l, m in [(missing_files, 'Missing file'), (missing_variables, 'Missing variable'), 
                 (missing_functions, 'Missing functions'), (wrong_functions, 'Wrong function pattern')]:
        for v in l:
            print(f'{m}: {v}')
        if l:
            print()
    if missing_files or missing_variables:
        raise VerificationError()