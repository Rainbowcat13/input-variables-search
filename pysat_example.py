from pysat.card import *
from pysat.formula import CNF
from pysat.solvers import Glucose3


formula = CNF(from_file='formula.cnf')
number_vars = formula.nv
g = Glucose3(formula.clauses)
minimal_set = [i + 1 for i in range(number_vars)]

for i in range(1, 2 ** number_vars):
    assumptions = [j + 1 for j in range(number_vars) if j & i]
    set_size = len(assumptions)
    for n in range(2 ** set_size):
        assumptions_with_signs = [-assumptions[j] for j in range(set_size) if n & j]
        no_conflicts, result = g.propagate(assumptions_with_signs)
        if no_conflicts and len(result) == number_vars:
            if set_size < len(minimal_set):
                minimal_set = assumptions + []

print(len(minimal_set))
print(*minimal_set)
