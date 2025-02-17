from pysat.formula import CNF
from pysat.solvers import Glucose3
from util import fullscan_values


formula = CNF(from_file='formula.cnf')
number_vars = formula.nv
g = Glucose3(formula.clauses)
minimal_set = [i + 1 for i in range(number_vars)]
prop_cnt = 0

for i in range(1, 2 ** number_vars):
    assumptions = [j + 1 for j in range(number_vars) if (2 ** j) & i]
    set_size = len(assumptions)
    for assumptions_with_signs in fullscan_values(assumptions, set_size):
        no_conflicts, result = g.propagate(assumptions_with_signs)
        prop_cnt += 1
        if not no_conflicts or len(result) != number_vars:
            break
    else:
        if set_size < len(minimal_set):
            minimal_set = assumptions + []

print(len(minimal_set))
print(*minimal_set)
print(f'Complexity: {prop_cnt}')
