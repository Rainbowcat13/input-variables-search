from pysat.formula import CNF
from pysat.solvers import Glucose3

from util import assumption_key


formula = CNF(from_file='formula.cnf')
number_vars = formula.nv
controversions_or_scanned = set()
non_output = set()
g = Glucose3(formula.clauses)
prop_cnt = 0
minimal_set = [i + 1 for i in range(number_vars)]
# Идея в том, чтобы перебирать переменные так, что если был найден набор с противоречиями,
# не перебирать никакие наборы, содержащие этот


def scan(not_used, assumption):
    global prop_cnt
    fs_key = frozenset(assumption)

    if fs_key in controversions_or_scanned:
        return

    abs_key = frozenset(assumption_key(assumption))
    if abs_key not in non_output:
        prop_cnt += 1
        no_conflicts, result = g.propagate(assumption)
        if not no_conflicts:
            controversions_or_scanned.add(fs_key)
            non_output.add(abs_key)
            return
        if len(result) < number_vars:
            non_output.add(abs_key)

    for var_num in not_used:
        for sign in [1, -1]:
            assumption.append(sign * var_num)
            not_used.remove(var_num)
            scan(not_used, assumption)
            not_used.add(var_num)
            assumption.pop()

    controversions_or_scanned.add(fs_key)


not_used_start = set(range(1, number_vars + 1))
scan(not_used_start, [])
for i in range(2 ** number_vars):
    assumptions = [j + 1 for j in range(number_vars) if (2 ** j) & i]
    if frozenset(assumptions) not in non_output and len(assumptions) < len(minimal_set):
        minimal_set = assumptions + []

print(len(minimal_set))
print(*minimal_set)
print(f'Complexity: {prop_cnt}')
