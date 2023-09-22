import os
import inspect

PRINT_FORMAT = '{:<50}{}'
CORRECT_STATE = 'OK'
WRONG_STATE = 'NOT OK'

files_to_verify = [
    os.path.join('verify.py'),
    os.path.join('exercise_1.py'),
    [os.path.join('exercise_1.md'), os.path.join('exercise_1.ipynb')],
    os.path.join('exercise_2.py'),
    # path to file
]

variables_to_verify = [
    ('exercise_1', 'data'),
    # tuple of (package, var name)
]

functions_to_verify = [
    # tuple of (package, function name, number of args)
    ('exercise_1', 'store_data', 1),
    ('exercise_1', 'get_data', 1),
    ('exercise_1', 'heartbeat', 2),
    
    ('exercise_2', 'compile_and_test_ast', 3),
    ('exercise_2', 'fib', 1),
    ('exercise_2', 'fib_test_simple', 0),
]

def verify_files():
    missing_files = list()
    for path in files_to_verify:
        if isinstance(path, list):
            or_paths = ' or '.join(path)
            if any([os.path.exists(p) for p in path]):
                state = CORRECT_STATE
            else:
                missing_files.append(or_paths)
                state = WRONG_STATE
            print(PRINT_FORMAT.format(or_paths, state))
        else:
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