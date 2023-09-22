from types import CodeType
from typing import Callable, List

def all_test_functions(module) -> List[Callable]:
    ts = [getattr(module, m) for m in dir(module) if m.startswith('test_')]
    assert len(ts) > 0
    for t in ts:
        assert t.__doc__ in ['+', '-']
    return ts

def get_positive_tests(module) -> List[CodeType]:
    return [t.__code__ for t in all_test_functions(module) if t.__doc__ == '+']

def get_negative_tests(module) -> List[CodeType]:
    return [t.__code__ for t in all_test_functions(module) if t.__doc__ == '-']
