import sys

from pysat.formula import CNF
from pysat.solvers import Glucose3


sys.setrecursionlimit(10 ** 9)


formula = CNF(from_file='formula.cnf')
number_vars = formula.nv
g = Glucose3(formula.clauses)
found = False
prop_cnt = 0
minimal_set = [i + 1 for i in range(number_vars)]


def scan(n, generated):
    global prop_cnt, minimal_set

    if len(generated) == n:
        prop_cnt += 1
        assumption = [generated[i] * (i + 1) for i in range(n) if generated[i]]
        no_conflicts, result = g.propagate(assumption)
        if no_conflicts and len(result) == number_vars:
            if len(minimal_set) > len(assumption):
                minimal_set = [abs(x) for x in assumption]
        return

    for var_value in range(-1, 2):
        generated.append(var_value)
        scan(n, generated)
        generated.pop()


scan(number_vars, [])
print(len(minimal_set))
print(*minimal_set)
print(f'Complexity: {prop_cnt}')
