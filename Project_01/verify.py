import atexit
import inspect
import os

PRINT_FORMAT = '{:<70}{}'
CORRECT_STATE = 'OK'
WRONG_STATE = 'NOT OK'

files_to_verify = [
    os.path.join('verify.py'),
    os.path.join('fault_localization.py'),
    os.path.join('fault_localization_tests.py'),
    os.path.join('slicer_statistical_debugging.py'),
    os.path.join('slicer_statistical_debugging_tests.py'),
    os.path.join('lib.py'),
    os.path.join('lib_fl.py'),
    # path to file
]

variables_to_verify = [
    ('lib', '_data'),
    ('slicer_statistical_debugging', 'DependencyDict'),
    ('slicer_statistical_debugging', 'Instrumenter'),
    ('slicer_statistical_debugging', 'DependencyCollector'),
    ('slicer_statistical_debugging', 'CoverageDependencyCollector'),
    ('slicer_statistical_debugging', 'DependencyDebugger'),
    ('fault_localization', 'Instrumenter'),
    ('fault_localization', 'FaultLocalization'),
    # tuple of (package, var name)
]

functions_to_verify = [
    ('lib', 'dump_data', 0),
    ('slicer_statistical_debugging', 'Instrumenter.instrument', 5),
    ('slicer_statistical_debugging', 'DependencyCollector.__init__', 2),
    ('slicer_statistical_debugging', 'DependencyCollector.collect', 2),
    ('slicer_statistical_debugging', 'DependencyCollector.events', 1),
    ('slicer_statistical_debugging', 'DependencyCollector.__enter__', 1),
    ('slicer_statistical_debugging', 'DependencyCollector.__exit__', 4),
    ('slicer_statistical_debugging', 'CoverageDependencyCollector.events', 1),
    ('slicer_statistical_debugging', 'DependencyDebugger.__init__', 3),
    ('fault_localization', 'Instrumenter.instrument', 5),
    ('fault_localization', 'FaultLocalization.__init__', 3),
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


def verify_variables():
    _missing_variables = list()
    current_package = None
    for package, variable in variables_to_verify:
        if current_package is None or current_package.__name__ != package:
            current_package = __import__(package)
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


def _delete_dump():
    if os.path.exists(os.path.join(os.getcwd(), 'dump')):
        os.remove(os.path.join(os.getcwd(), 'dump'))
        assert not os.path.exists(os.path.join(os.getcwd(), 'dump'))


if __name__ == '__main__':
    atexit.register(_delete_dump)
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
