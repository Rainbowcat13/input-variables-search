import sys

from pysat.formula import CNF
from pysat.solvers import Glucose3

from util import assumption_key


sys.setrecursionlimit(10 ** 9)


formula = CNF(from_file='formula.cnf')
number_vars = formula.nv
g = Glucose3(formula.clauses)
found = False
prop_cnt = 0
minimal_set = [i + 1 for i in range(number_vars)]
miss_count = dict()


def scan(n, generated):
    global prop_cnt, minimal_set

    if len(generated) == n:
        assumption = [generated[i] * (i + 1) for i in range(n) if generated[i]]
        key = frozenset(assumption_key(assumption))
        if miss_count.get(key) is not None:
            return
        no_conflicts, result = g.propagate(assumption)
        prop_cnt += 1
        if not no_conflicts or len(result) != number_vars:
            miss_count[key] = True
        return

    for var_value in range(-1, 2):
        generated.append(var_value)
        scan(n, generated)
        generated.pop()


scan(number_vars, [])
for i in range(2 ** number_vars):
    assumptions = [j + 1 for j in range(number_vars) if (2 ** j) & i]
    if miss_count.get(frozenset(assumptions)) is None and len(assumptions) < len(minimal_set):
        minimal_set = assumptions + []

print(len(minimal_set))
print(*minimal_set)
print(f'Complexity: {prop_cnt}')
