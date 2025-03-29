from __future__ import annotations

import math

from pysat.formula import CNF
from pysat.solvers import Glucose3, Cadical195
import numpy as np

from itertools import combinations
from collections import Counter


def fullscan_values(assumption, set_size):
    assumption = list(assumption)
    for n in range(2 ** set_size):
        yield [-assumption[j] if (n & (2 ** j)) > 0 else assumption[j] for j in range(set_size)]


def assumption_key(assumption):
    return list(map(abs, assumption))


def precount_set_order(formula: CNF, solver: Glucose3 | Cadical195, level=2):
    assumptions = list(combinations(list(range(1, formula.nv + 1)), level))
    assumptions_count = len(assumptions)
    outputs = [0] * assumptions_count
    for index in range(assumptions_count):
        for assumption_with_signs in fullscan_values(assumptions[index], level):
            no_conflicts, result = solver.propagate(assumption_with_signs)
            outputs[index] += len(result)

    assumptions_with_result_powers = list(zip(assumptions, outputs))
    assumptions_with_result_powers.sort(key=lambda item: -item[1])
    return [list(item[0]) for item in assumptions_with_result_powers]


def var_frequency(formula: CNF):
    counter = Counter(assumption_key(sum(formula.clauses, [])))
    return {var_name: count for (var_name, count) in counter.most_common()}


def random_assumptions(vector: list[int], num_assumptions=None) -> list[list[int]]:
    n = len(vector)
    max_assumptions_number = 2 ** n
    if num_assumptions is None or num_assumptions > max_assumptions_number:
        num_assumptions = max_assumptions_number

    vector = np.array(vector)
    signs_mtr = np.where(np.random.rand(num_assumptions, n) < 0.5, 1, -1)
    assumptions = vector * signs_mtr
    return assumptions.tolist()


def fitness(solver: Glucose3 | Cadical195, candidate: list[int], estimation_vectors_count: int) -> (float, float):
    if math.log2(estimation_vectors_count) > len(candidate):
        estimation_vectors_count = 2 ** len(candidate)
    vectors = random_assumptions(candidate, estimation_vectors_count)

    metric = 0
    conflicts_count = 0
    for vector in vectors:
        no_conflicts, result = solver.propagate(vector)

        if not no_conflicts:
            conflicts_count += 1
            # return -1, -1
        else:
            metric += len(result)

    ratio = (
        # metric / (estimation_vectors_count - conflicts_count) if conflicts_count < estimation_vectors_count else 0,
        metric / estimation_vectors_count,
        conflicts_count / estimation_vectors_count
    )
    return ratio


def formula_size(f: CNF) -> int:
    return sum([len(clause) for clause in f.clauses])


if __name__ == '__main__':
    formula = CNF(from_file='formula.cnf')
    g = Glucose3(formula.clauses)
    print(precount_set_order(formula, g, level=3))
    print(var_frequency(formula))
