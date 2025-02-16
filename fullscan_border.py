from itertools import combinations
from util import fullscan_values
from pysat.formula import CNF
from pysat.solvers import Glucose3


formula = CNF(from_file='formula.cnf')
number_vars = formula.nv
g = Glucose3(formula.clauses)
found = False
prop_cnt = 0


for count in range(1, number_vars):
    assumptions = list(combinations(range(1, number_vars + 1), count))
    for assumption in assumptions:
        for assumption_with_signs in fullscan_values(assumption, count):
            prop_cnt += 1
            no_conflicts, result = g.propagate(assumption_with_signs)
            if no_conflicts and len(result) == number_vars:
                print(count)
                print(*assumption)
                found = True
                break
        if found:
            break

    if found:
        break
else:
    print(number_vars)
    print(*[i + 1 for i in range(number_vars)])

print(f'Complexity: {prop_cnt}')
