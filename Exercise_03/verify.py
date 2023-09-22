import os
import inspect

PRINT_FORMAT = '{:<40}{}'
CORRECT_STATE = 'OK'
WRONG_STATE = 'NOT OK'

files_to_verify = [
    os.path.join('verify.py'),
    os.path.join('exercise_1.py'),
    os.path.join('exercise_2.py'),
    os.path.join('exercise_3.py'),
    # path to file
]

variables_to_verify = [
    ('exercise_1', 'data'),
    ('exercise_3', 'Train'),
    ('exercise_3', 'Track'),
    ('exercise_3', 'Station'),
    ('exercise_3', 'TrainNetwork'),
    # tuple of (package, var name)
]

functions_to_verify = [
    # tuple of (package, function name, number of args)
    ('exercise_1', 'store_data', 1),
    ('exercise_1', 'get_data', 1),
    ('exercise_1', 'heartbeat', 2),
    ('exercise_2', 'assert_equal', 2),
    ('exercise_2', 'assert_not_equal', 2),
    ('exercise_2', 'assert_true', 1),
    ('exercise_2', 'assert_false', 1),
    ('exercise_2', 'assert_is', 2),
    ('exercise_2', 'assert_is_not', 2),
    ('exercise_2', 'assert_is_none', 1),
    ('exercise_2', 'assert_is_not_none', 1),
    ('exercise_2', 'assert_is_in', 2),
    ('exercise_2', 'assert_is_not_in', 2),
    ('exercise_2', 'assert_is_instance', 2),
    ('exercise_2', 'assert_is_not_instance', 2),
    ('exercise_3', 'Train.__init__', 2),
    ('exercise_3', 'Track.repOK', 1),
    ('exercise_3', 'Track.__init__', 4),
    ('exercise_3', 'Track.set_train', 2),
    ('exercise_3', 'Track.remove_train', 1),
    ('exercise_3', 'Station.repOK', 1),
    ('exercise_3', 'Station.__init__', 2),
    ('exercise_3', 'Station.add_track', 2),
    ('exercise_3', 'TrainNetwork.repOK', 1),
    ('exercise_3', 'TrainNetwork.__init__', 4),
    ('exercise_3', 'TrainNetwork.add_station', 2),
    ('exercise_3', 'TrainNetwork.add_track', 2),
    ('exercise_3', 'TrainNetwork.add_train', 2),
    ('exercise_3', 'TrainNetwork.move_train', 4),
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