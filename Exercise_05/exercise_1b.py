from debuggingbook.StatisticalDebugger import Collector
from types import FrameType
from typing import Any, Dict
import inspect

from predicate import Predicate

def ackermann(m, n):
    if m == 0:
        return n + 1
    elif n == 0:
        return ackermann(m - 1, 1)
    else:
        return ackermann(m - 1, ackermann(m, n - 1))


class PredicateCollector(Collector):

    def __init__(self) -> None:
        super().__init__()
        self.predicates: Dict[str, Predicate] = dict()

    def collect(self, frame: FrameType, event: str, arg: Any) -> None:
        frame_values = inspect.getargvalues(frame)
        func_name = frame.f_code.co_name
        for arg in frame_values.args:
            if not isinstance(frame_values.locals[arg], int) and not isinstance(frame_values.locals[arg], float):
                break
            if frame_values.locals[arg] == 0:
                self.predicates.update({f"{func_name}({arg} == 0)": Predicate(rpr=f"{func_name}({arg} == 0)", true=1, observed=1)})
                self.predicates.update({f"{func_name}({arg} < 0)": Predicate(rpr=f"{func_name}({arg} < 0)", true=0, observed=1)})
                self.predicates.update({f"{func_name}({arg} > 0)": Predicate(rpr=f"{func_name}({arg} > 0)", true=0, observed=1)})
            elif frame_values.locals[arg] < 0:
                self.predicates.update({f"{func_name}({arg} == 0)": Predicate(rpr=f"{func_name}({arg} == 0)", true=0, observed=1)})
                self.predicates.update({f"{func_name}({arg} < 0)": Predicate(rpr=f"{func_name}({arg} < 0)", true=1, observed=1)})
                self.predicates.update({f"{func_name}({arg} > 0)": Predicate(rpr=f"{func_name}({arg} > 0)", true=0, observed=1)})
            elif frame_values.locals[arg] > 0:
                self.predicates.update({f"{func_name}({arg} == 0)": Predicate(rpr=f"{func_name}({arg} == 0)", true=0, observed=1)})
                self.predicates.update({f"{func_name}({arg} < 0)": Predicate(rpr=f"{func_name}({arg} < 0)", true=0, observed=1)})
                self.predicates.update({f"{func_name}({arg} > 0)": Predicate(rpr=f"{func_name}({arg} > 0)", true=1, observed=1)})
            for arg2 in frame_values.args:
                if not isinstance(frame_values.locals[arg2], int) and not isinstance(frame_values.locals[arg2], float):
                    continue
                if arg == arg2:
                    continue
                if frame_values.locals[arg] == frame_values.locals[arg2]:
                    self.predicates.update({f"{func_name}({arg} == {arg2})": Predicate(rpr=f"{func_name}({arg} == {arg2})", true=1, observed=1)})
                    self.predicates.update({f"{func_name}({arg2} == {arg})": Predicate(rpr=f"{func_name}({arg2} == {arg})", true=1, observed=1)})
                    self.predicates.update({f"{func_name}({arg} > {arg2})": Predicate(rpr=f"{func_name}({arg} > {arg2})", true=0, observed=1)})
                    self.predicates.update({f"{func_name}({arg2} < {arg})": Predicate(rpr=f"{func_name}({arg2} < {arg})", true=0, observed=1)})
                    self.predicates.update({f"{func_name}({arg} < {arg2})": Predicate(rpr=f"{func_name}({arg} < {arg2})", true=0, observed=1)})
                    self.predicates.update({f"{func_name}({arg2} > {arg})": Predicate(rpr=f"{func_name}({arg2} > {arg})", true=0, observed=1)})
                elif frame_values.locals[arg] < frame_values.locals[arg2]:
                    self.predicates.update({f"{func_name}({arg} == {arg2})": Predicate(rpr=f"{func_name}({arg} == {arg2})", true=0, observed=1)})
                    self.predicates.update({f"{func_name}({arg2} == {arg})": Predicate(rpr=f"{func_name}({arg2} == {arg})", true=0, observed=1)})
                    self.predicates.update({f"{func_name}({arg} > {arg2})": Predicate(rpr=f"{func_name}({arg} > {arg2})", true=0, observed=1)})
                    self.predicates.update({f"{func_name}({arg2} < {arg})": Predicate(rpr=f"{func_name}({arg2} < {arg})", true=0, observed=1)})
                    self.predicates.update({f"{func_name}({arg} < {arg2})": Predicate(rpr=f"{func_name}({arg} < {arg2})", true=1, observed=1)})
                    self.predicates.update({f"{func_name}({arg2} > {arg})": Predicate(rpr=f"{func_name}({arg2} > {arg})", true=1, observed=1)})
                elif frame_values.locals[arg] > frame_values.locals[arg2]:
                    self.predicates.update({f"{func_name}({arg} == {arg2})": Predicate(rpr=f"{func_name}({arg} == {arg2})", true=0, observed=1)})
                    self.predicates.update({f"{func_name}({arg2} == {arg})": Predicate(rpr=f"{func_name}({arg2} == {arg})", true=0, observed=1)})
                    self.predicates.update({f"{func_name}({arg} > {arg2})": Predicate(rpr=f"{func_name}({arg} > {arg2})", true=1, observed=1)})
                    self.predicates.update({f"{func_name}({arg2} < {arg})": Predicate(rpr=f"{func_name}({arg2} < {arg})", true=1, observed=1)})
                    self.predicates.update({f"{func_name}({arg} < {arg2})": Predicate(rpr=f"{func_name}({arg} < {arg2})", true=0, observed=1)})
                    self.predicates.update({f"{func_name}({arg2} > {arg})": Predicate(rpr=f"{func_name}({arg2} > {arg})", true=0, observed=1)})


def test_collection():
    with PredicateCollector() as pc:
        ackermann(0, 1)
    results = {
        'ackermann(m == 0)': (1, 1),
        'ackermann(m < 0)': (0, 1),
        'ackermann(m > 0)': (0, 1),
        'ackermann(m < n)':  (1, 1),
        'ackermann(m > n)':  (0, 1),
        'ackermann(n == 0)': (0, 1),
        'ackermann(n < 0)': (0, 1),
        'ackermann(n > 0)': (1, 1),
        'ackermann(n < m)':  (0, 1),
        'ackermann(n > m)':  (1, 1),
        'ackermann(m == n)': (0, 1),
        'ackermann(n == m)': (0, 1),
    }
    for pred in results:
        pred = pc.predicates[pred]
        p, o = results[pred.rpr]
        assert pred.true == p, f'True for {pred} was wrong, expected {p}, was {pred.true}'
        assert pred.observed == o, f'Observed for {pred} was wrong, expected {o}, was {pred.observed}'
        assert pred.failing_observed == pred.successful_observed == pred.failing_true == pred.successful_true == 0


if __name__ == '__main__':
    test_collection()
    print('Successful')
