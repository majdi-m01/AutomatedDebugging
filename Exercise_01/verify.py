import os
import inspect

PRINT_FORMAT = '{:<40}{}'
CORRECT_STATE = 'OK'
WRONG_STATE = 'NOT OK'

files_to_verify = [
    os.path.join('verify.py'),
    os.path.join('exercise_1.py'),
    os.path.join('exercise_1a.py'),
    os.path.join('exercise_1b.py'),
    os.path.join('exercise_2.py'),
    os.path.join('exercise_2a.py'),
    os.path.join('exercise_2b.py'),
    # path to file
]

variables_to_verify = [
    ('exercise_1', 'LEN'),
    ('exercise_1', 'BASE'),
    ('exercise_1', 'OFFSET'),
    ('exercise_1', 'CHAR_a'),
    ('exercise_1', 'CHAR_f'),
    ('exercise_1', 'CHAR_A'),
    ('exercise_1', 'CHAR_F'),
    ('exercise_1', 'CHAR_0'),
    ('exercise_1', 'CHAR_9'),
    ('exercise_1a', 'hex_str_assertion_error'),
    ('exercise_1a', 'hex_str_functional_error'),
    ('exercise_1b', 'LEN'),
    ('exercise_1b', 'BASE'),
    ('exercise_1b', 'OFFSET'),
    ('exercise_1b', 'CHAR_a'),
    ('exercise_1b', 'CHAR_f'),
    ('exercise_1b', 'CHAR_A'),
    ('exercise_1b', 'CHAR_F'),
    ('exercise_1b', 'CHAR_0'),
    ('exercise_1b', 'CHAR_9'),
    ('exercise_2a', 'RecursiveTracer'),
    ('exercise_2b', 'level'),
    # tuple of (package, var name)
]

functions_to_verify = [
    # tuple of (package, function name, number of args)
    ('exercise_1', 'check_lower', 1),
    ('exercise_1', 'check_upper', 1),
    ('exercise_1', 'check_number', 1),
    ('exercise_1', 'check', 1),
    ('exercise_1', 'convert_char', 1),
    ('exercise_1', 'convert_byte', 2),
    ('exercise_1', 'convert_string', 2),
    ('exercise_1', 'check_len', 1),
    ('exercise_1', 'convert_to_rgb', 1),
    ('exercise_1b', 'check_lower', 1),
    ('exercise_1b', 'check_upper', 1),
    ('exercise_1b', 'check_number', 1),
    ('exercise_1b', 'check', 1),
    ('exercise_1b', 'convert_char', 1),
    ('exercise_1b', 'convert_byte', 2),
    ('exercise_1b', 'convert_string', 2),
    ('exercise_1b', 'check_len', 1),
    ('exercise_1b', 'convert_to_rgb', 1),
    ('exercise_2', 'fib', 1),
    ('exercise_2', 'merge', 4),
    ('exercise_2', 'merge_sort', 3),
    ('exercise_2a', 'param_names', 1),
    ('exercise_2b', 'fib', 1),
    ('exercise_2b', 'merge', 4),
    ('exercise_2b', 'merge_sort', 3),
    ('exercise_2b', 'log', 1),
    ('exercise_2b', 'increase_level', 0),
    ('exercise_2b', 'decrease_level', 0),
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
        function_repr = f'{package}.{function}'
        if function in dir(current_package):
            specs = inspect.getfullargspec(getattr(current_package, function))
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