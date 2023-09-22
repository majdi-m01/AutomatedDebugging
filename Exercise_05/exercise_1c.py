from debuggingbook.StatisticalDebugger import DifferenceDebugger
from typing import Optional, Set, Any

from predicate import Predicate
from exercise_1a import failure, context, increase
from exercise_1b import PredicateCollector, ackermann

class PredicateDebugger(DifferenceDebugger):
    
    def __init__(self, log: bool = False):
        super().__init__(collector_class=PredicateCollector, log=log)
    
    def all_predicates(self) -> Set[Any]:
        """Return a set of all predicates observed."""
        passed_list = []
        updated_passed_list = []
        for passed_item in self.collectors.get('PASS'):
            for key, value in passed_item.predicates.items():
                passed_list.append(value)
        for value in passed_list:
            if value in updated_passed_list:
                for new in updated_passed_list:
                    if value.rpr == new.rpr:
                        new.successful_observed += 1
                        if value.true == 1:
                            new.successful_true += 1
            else:
                updated_passed_list.append(value)
                i = updated_passed_list.index(value)
                updated_passed_list[i].successful_observed += 1
                updated_passed_list[i].successful_true += 1

        failed_list = []
        updated_failed_list = []
        for failed_item in self.collectors.get('FAIL'):
            for key, value in failed_item.predicates.items():
                failed_list.append(value)
        for value in failed_list:
            if value in updated_failed_list:
                for new in updated_failed_list:
                    if value.rpr == new.rpr:
                        new.failing_observed += 1
                        if value.true == 1:
                            new.failing_true += 1
            else:
                updated_failed_list.append(value)
                i = updated_failed_list.index(value)
                updated_failed_list[i].failing_observed += 1
                if value.true == 1:
                    updated_failed_list[i].failing_true += 1

        complete_set = []
        for p in updated_passed_list:
            for f in updated_failed_list:
                if p.rpr == f.rpr:
                    complete_set.append(Predicate(p.rpr,
                                       p.failing_true + f.failing_true,
                                       p.successful_true + f.successful_true,
                                       0,
                                       p.failing_observed + f.failing_observed,
                                       p.successful_observed + f.successful_observed,
                                       0))
        for e in complete_set:
            e.true = e.failing_true + e.successful_true
            e.observed = e.failing_observed + e.successful_observed

        return set(complete_set)
    

def test_debugger():
    epsilon = 0.000001
    results = {
        'ackermann(m == 0)': (1/3, 1/3, 0),
        'ackermann(m < 0)':  (0,   1/3, -1/3),
        'ackermann(m > 0)':  (0,   1/3, -1/3),
        'ackermann(m < n)':  (0.5, 1/3, 0.5 - 1/3),
        'ackermann(m > n)':  (0,   1/3, -1/3),
        'ackermann(n == 0)': (0,   1/3, -1/3),
        'ackermann(n < 0)':  (0,   1/3, -1/3),
        'ackermann(n > 0)':  (0.5, 1/3, 0.5 - 1/3),
        'ackermann(n < m)':  (0,   1/3, -1/3),
        'ackermann(n > m)':  (0.5, 1/3, 0.5 - 1/3),
        'ackermann(m == n)': (0,   1/3, -1/3),
        'ackermann(n == m)': (0,   1/3, -1/3),
    }
    pd = PredicateDebugger()

    with pd.collect_pass():
        ackermann(3, 3)
    with pd.collect_pass():
        ackermann(0, 0)
    with pd.collect_fail():
        ackermann(0, 1)
    
    preds = pd.all_predicates()
    
    for p in results:
        assert Predicate(p) in preds, f'{p} not in all_predicates() result'
        
    for p in preds:
        f, c, i = results[p.rpr]
        assert abs(failure(p) - f) < epsilon, f'Failure for {p} was wrong, expected {f}, was {failure(p)}' 
        assert abs(context(p) - c) < epsilon, f'Context for {p} was wrong, expected {c}, was {context(p)}' 
        assert abs(increase(p) - i) < epsilon, f'Increase for {p} was wrong, expected {i}, was {increase(p)}' 
        

if __name__ == '__main__':
    test_debugger()
    print('Successful')
