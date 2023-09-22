import os
import inspect

PRINT_FORMAT = '{:<50}{}'
CORRECT_STATE = 'OK'
WRONG_STATE = 'NOT OK'

files_to_verify = [
    os.path.join('exercise_1.py'),
    os.path.join('exercise_2.py'),
    # path to file
]

variables_to_verify = [
    # tuple of (package, var name)
    ('exercise_1', 'TESTCASES')
]

functions_to_verify = [
    # tuple of (package, function name, number of args)
    ('exercise_1', 'search_buggy_1', 2),
    ('exercise_1', 'search_buggy_2', 2),
    ('exercise_1', 'search_correct', 2),
    ('exercise_1', 'search_buggy_1_test', 3),
    ('exercise_1', 'search_buggy_2_test', 3),

    ('exercise_2', 'comparator_mutation_candidates', 1),
    ('exercise_2', 'collect_atomic_conditions', 1),
    ('exercise_2', 'test_comparator_mutation_candidates', 2),
    ('exercise_2', 'test_a', 0),
    ('exercise_2', 'should_sample', 2),
    ('exercise_2', 'a_loop', 2),
    ('exercise_2', 'test_b', 0),
    ('exercise_2', 'sort_by_second_descending', 1),
    ('exercise_2', 'sort_by_second_descending_test', 2),
    ('exercise_2', 'test_c_1', 0),
    ('exercise_2', 'multiple_2_3_5', 1),
    ('exercise_2', 'multiple_2_3_5_test', 1),
    ('exercise_2', 'test_c_2', 0),
]

classes_to_verify = [
    # tuple of (package, class name, a name list of required members)
    ('exercise_2', 'ConditionGenerator', ['__init__', 'sample']),
    ('exercise_2', 'ConditionMutator',
        ['__init__', 'mutate', 'choose_op', 'choose_bool_op', 'swap']),
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

def verify_classes():
    missing_classes = list()
    missing_members = list()
    current_package = None
    state = CORRECT_STATE

    for package, clazz, members in classes_to_verify:
        if current_package is None or current_package.__name__ != package:
            current_package = __import__(package)
        class_repr = f'{package}.{clazz}'
        if clazz in dir(current_package):
            for member in members:
                if member not in dir(getattr(current_package, clazz)):
                    member_repr = f'{package}.{clazz}.{member}'
                    missing_members.append(member_repr)
                    state = WRONG_STATE
        else:
            missing_classes.append(class_repr)
            state = WRONG_STATE
        print(PRINT_FORMAT.format(class_repr, state))
    print()
    return missing_classes, missing_members

class VerificationError(ValueError):
    pass

if __name__ == '__main__':
    missing_files = verify_files()
    missing_variables = verify_variables()
    missing_functions, wrong_functions = verify_functions()
    missing_classes, missing_members = verify_classes() if classes_to_verify else ([], [])

    for l, m in [(missing_files, 'Missing file'), (missing_variables, 'Missing variable'), 
                 (missing_functions, 'Missing functions'), (wrong_functions, 'Wrong function pattern'),
                 (missing_classes, 'Missing classes'), (missing_members, 'Missing members')]:
        for v in l:
            print(f'{m}: {v}')
        if l:
            print()
    if missing_files or missing_variables or missing_classes:
        raise VerificationError()