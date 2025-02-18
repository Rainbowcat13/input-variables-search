from pysat.formula import CNF
from pysat.solvers import Glucose3

from itertools import combinations


def fullscan_values(assumption, set_size):
    assumption = list(assumption)
    for n in range(2 ** set_size):
        yield [-assumption[j] if (n & (2 ** j)) > 0 else assumption[j] for j in range(set_size)]


def assumption_key(assumption):
    return list(map(abs, assumption))


def precount_set_order(formula: CNF, solver: Glucose3, level=2):
    assumptions = list(combinations(list(range(1, formula.nv + 1)), level))
    assumptions_count = len(assumptions)
    outputs = [0] * assumptions_count
    for index in range(assumptions_count):
        for assumption_with_signs in fullscan_values(assumptions[index], level):
            no_conflicts, result = solver.propagate(assumption_with_signs)
            outputs[index] += len(result)

    assumptions_with_result_powers = list(zip(assumptions, outputs))
    assumptions_with_result_powers.sort(key=lambda item: -item[1])
    return [item[0] for item in assumptions_with_result_powers]


if __name__ == '__main__':
    formula = CNF(from_file='formula.cnf')
    g = Glucose3(formula.clauses)
    print(precount_set_order(formula, g, level=3))
