import inspect
import os

PRINT_FORMAT = '{:<70}{}'
CORRECT_STATE = 'OK'
WRONG_STATE = 'NOT OK'

files_to_verify = [
    os.path.join('verify.py'),
    os.path.join('repair', '__init__.py'),
    os.path.join('repair', 'mutator.py'),
    os.path.join('repair', 'synthesizer.py'),
    os.path.join('repair', 'tester.py'),
    os.path.join('repair', 'repairer.py'),
    # path to file
]

variables_to_verify = [
    ('repair.mutator', 'Marker'),
    ('repair.mutator', 'MutationOperator'),
    ('repair.mutator', 'Tighten'),
    ('repair.mutator', 'Loosen'),
    ('repair.mutator', 'Guard'),
    ('repair.mutator', 'Break'),
    ('repair.mutator', 'Mutator'),

    ('repair.synthesizer', 'Template'),
    ('repair.synthesizer.Template', 'NameTransformer'),
    ('repair.synthesizer', 'Synthesizer'),

    ('repair.tester', 'Env'),
    ('repair.tester', 'Record'),
    ('repair.tester', 'Context'),
    ('repair.tester', 'THE_CONTEXT_OBJECT'),
    ('repair.tester', 'Instantiate'),

    ('repair.repairer', 'Repairer'),
    # tuple of (package, var name)
]

functions_to_verify = [
    ('repair.mutator.Marker', '__init__', 2),
    ('repair.mutator.Marker', 'generic_visit', 2),

    ('repair.mutator', 'mk_abstract', 0),
    ('repair.mutator.MutationOperator', '__init__', 1),
    ('repair.mutator.Break', '__init__', 2),

    ('repair.mutator.Mutator', '__init__', 4),
    ('repair.mutator.Mutator', 'apply', 2),

    ('repair.synthesizer.Template', '__init__', 3),
    ('repair.synthesizer.Template', 'from_lambda', 2),
    ('repair.synthesizer.Template', 'instantiate', 2),

    ('repair.synthesizer.Synthesizer', '__init__', 7),
    ('repair.synthesizer.Synthesizer', 'apply', 1),
    ('repair.synthesizer.Synthesizer', 'flip', 2),
    ('repair.synthesizer.Synthesizer', 'solve', 2),
    ('repair.synthesizer.Synthesizer', 'sat', 3),
    ('repair.synthesizer.Synthesizer', 'validate', 1),
    ('repair.synthesizer', 'no_log', 1),

    ('repair.tester.Record', '__init__', 3),
    ('repair.tester.Record', '__add__', 2),
    ('repair.tester.Record', '__repr__', 1),

    ('repair.tester.Context', '__init__', 2),
    ('repair.tester.Context', 'next_value', 2),
    
    ('repair.tester.Instantiate', '__init__', 2),
    ('repair.tester.Instantiate', 'visit_Name', 2),

    ('repair.tester', 'mk_expr', 1),
    ('repair.tester', 'exec_abstract', 3),
    ('repair.tester', 'all_true', 0),
    ('repair.tester', 'run_tests', 3),

    ('repair.repairer.Repairer', '__init__', 8),
    ('repair.repairer.Repairer', 'repair', 1),
    ('repair.repairer.Repairer', 'validate', 2),
    # tuple of (package, function name, number of args)
]

def verify_files():
    _missing_files = list()
    for path in files_to_verify:
        if os.path.exists(path):
            state = CORRECT_STATE
        else:
            _missing_files.append(path)
            state = WRONG_STATE
        print(PRINT_FORMAT.format(path, state))
    print()
    return _missing_files

from importlib import import_module

def import_module_or_class(path: str):
    try:
        m = import_module(path)
    except ModuleNotFoundError:
        parts = path.split('.')
        base = '.'.join(parts[:-1])
        cls = parts[-1]
        return getattr(import_module(base), cls)

    return m

def verify_variables():
    _missing_variables = list()
    current_package = None
    for package, variable in variables_to_verify:
        if current_package is None or current_package.__name__ != package:
            current_package = import_module_or_class(package)
        variable_repr = f'{package}.{variable}'
        if variable in dir(current_package):
            state = CORRECT_STATE
        else:
            _missing_variables.append(variable_repr)
            state = WRONG_STATE
        print(PRINT_FORMAT.format(variable_repr, state))
    print()
    return _missing_variables

def verify_functions():
    _missing_functions = list()
    _wrong_functions = list()
    current_package = None
    for package, function, args in functions_to_verify:
        if current_package is None or current_package.__name__ != package:
            current_package = import_module_or_class(package)
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
                _wrong_functions.append(function_repr)
                state = WRONG_STATE
        else:
            _missing_functions.append(function_repr)
            state = WRONG_STATE
        print(PRINT_FORMAT.format(function_repr, state))
    print()
    return _missing_functions, _wrong_functions


class VerificationError(ValueError):
    pass

if __name__ == '__main__':
    missing_files = verify_files()
    missing_variables = verify_variables()
    missing_functions, wrong_functions = verify_functions()
    for file_list, msg in [(missing_files, 'Missing file'), (missing_variables, 'Missing variable'),
                           (missing_functions, 'Missing functions'), (wrong_functions, 'Wrong function pattern')]:
        for v in file_list:
            print(f'{msg}: {v}')
        if file_list:
            print()
    if missing_files or missing_variables:
        raise VerificationError()
