class Predicate:
    
    def __init__(self, rpr: str, failing_true: int = 0,  
                 successful_true: int = 0, true: int = 0, failing_observed: int = 0, 
                 successful_observed: int = 0, observed: int = 0):
        self.rpr = rpr
        self.failing_observed = failing_observed
        self.successful_observed = successful_observed
        self.observed = observed
        self.failing_true = failing_true
        self.successful_true = successful_true
        self.true = true
        
    def __repr__(self):
        return (f'{self.rpr}(F(p)={self.failing_true}, S(p)={self.successful_true}), ‚' 
                f'F(p observed)={self.failing_observed}), S(p observed)={self.successful_observed}, p={self.true}, p observed={self.observed}))')
    
    def __str__(self):
        return self.__repr__()
    
    def __hash__(self):
        return hash(self.rpr)
    
    def __eq__(self, other):
        return isinstance(other, Predicate) and self.rpr == other.rpr
    
