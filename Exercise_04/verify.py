import os
import inspect

PRINT_FORMAT = '{:<40}{}'
CORRECT_STATE = 'OK'
WRONG_STATE = 'NOT OK'

files_to_verify = [
    os.path.join('verify.py'),
    os.path.join('exercise_1.py'),
    os.path.join('exercise_2.py'),
    # path to file
]

variables_to_verify = [
    ('exercise_1', 'Transformer'),
    ('exercise_2', 'Reducer'),
    ('exercise_2', 'ReduceSlicer'),
    # tuple of (package, var name)
]

functions_to_verify = [
    # tuple of (package, function name, number of args)
    ('exercise_1', 'fib', 1),
    ('exercise_1', 'merge', 4),
    ('exercise_1', 'merge_sort', 3),
    ('exercise_1', 'parse_expr', 1),
    ('exercise_1', 'parse_stmt', 1),
    ('exercise_1', 'log', 0),
    ('exercise_1', 'returned', 2),
    ('exercise_1', 'Transformer.visit_FunctionDef', 2),
    ('exercise_1', 'call_traced', 1),
    ('exercise_1', 'with_indent', 2),
    
    ('exercise_2', 'Reducer.__init__', 2),
    ('exercise_2', 'Reducer.generic_visit', 2),
    ('exercise_2', 'ReduceSlicer.reduce', 2),
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