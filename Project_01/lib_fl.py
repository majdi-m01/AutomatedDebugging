import atexit
import pickle

from fault_localization import FaultLocalization

_data = FaultLocalization()


def dump_data():
    data = dict()
    data['data'] = set()
    data['control'] = set()
    for name, (func, line) in _data.dependencies().data:
        data['data'].add(((name, (func.__name__, line)),
                          tuple(sorted([(n, (f.__name__, l))
                                        for n, (f, l) in _data.dependencies().data[(name, (func, line))]]))))
    for name, (func, line) in _data.dependencies().control:
        data['control'].add(((name, (func.__name__, line)),
                             tuple(sorted([(n, (f.__name__, l))
                                           for n, (f, l) in _data.dependencies().control[(name, (func, line))]]))))
    with open('dump', 'wb') as fp:
        pickle.dump(data, fp)


atexit.register(dump_data)
