from __future__ import annotations

import math
import os
import random
import sys
import time
from enum import Enum
from functools import wraps
from pathlib import Path

import numpy as np
from pysat.formula import CNF
from pysat.solvers import Glucose3, Cadical195

from collections import Counter
from itertools import combinations


class ScoreMethod(Enum):
    CONFLICTS = 1
    PROP = 2
    TOTAL = 3


class CNFSchema:
    def __init__(self, cnf: CNF, inputs: list[int], outputs: list[int]):
        self.cnf = cnf
        self.inputs = inputs
        self.outputs = outputs


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


def fitness(solver_or_formula: Glucose3 | Cadical195 | CNF, candidate: list[int], estimation_vectors_count: int,
            zero_conflict_tolerance=False) -> (float, float):
    solver = solver_or_formula
    if isinstance(solver_or_formula, CNF):
        solver = Glucose3(bootstrap_with=solver_or_formula.clauses)

    if math.log2(estimation_vectors_count) > len(candidate):
        estimation_vectors_count = 2 ** len(candidate)
    vectors = random_assumptions(candidate, estimation_vectors_count)

    metric = 0
    conflicts_count = 0
    for vector in vectors:
        no_conflicts, result = solver.propagate(vector)

        if not no_conflicts:
            conflicts_count += 1
            if zero_conflict_tolerance:
                return -0.1, 1.01
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


def extremum_indices(ratios: list[float]) -> list[int]:
    result = []
    for index in range(1, len(ratios) - 1):
        if ratios[index] >= ratios[index - 1] and ratios[index] > ratios[index + 1]:
            result.append(index)
    return result


def extract_filenames(dirs, extension):
    return [
        str(file.absolute())
        for file in sum([
            list(Path(d).glob('**/*'))
            for d in dirs
        ], [])
        if file.name.endswith(extension)
    ]


def basename_noext(filename):
    return os.path.splitext(os.path.basename(filename))[0]


def mkdirs(*dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def total_ratio(f: CNF, prop_ratio: float, conflict_ratio: float) -> float:
    return prop_ratio / f.nv * (1 - conflict_ratio)


def count_total_ratio(f: CNF, solver: Glucose3 | Cadical195, cand, estimation_vector_count=200):
    prop_ratio, conflict_ratio = fitness(solver, cand, estimation_vector_count)
    return total_ratio(f, prop_ratio, conflict_ratio)


def score(f: CNF, s: Glucose3 | Cadical195, cand: list[int],
          estimation_vector_count: int, method: ScoreMethod):
    if method == ScoreMethod.PROP:
        return fitness(s, cand, estimation_vector_count)[0] / f.nv
    elif method == ScoreMethod.CONFLICTS:
        return -fitness(s, cand, estimation_vector_count)[1]
    elif method == ScoreMethod.TOTAL:
        return count_total_ratio(f, s, cand, estimation_vector_count)
    else:
        raise ValueError('Unknown score method')


def xor_cnf(a: int, b: int, c: int) -> list[list[int]]:
    return [
        [a, b, -c], [-a, -b, -c], [a, -b, c], [-a, b, c]
    ]


def transform_variable(f: CNF, var: int, ignore: bool, offset: int):
    if ignore or var == 0:
        return var
    return var + f.nv - offset if var > 0 else var - f.nv + offset


def unite_variables(f: CNF, var_list: list[int], ignore: list[int] = None, offset: int = 0) -> list[int]:
    if ignore is None:
        ignore = set()
    else:
        ignore = set(ignore)
    return [
        transform_variable(f, var, abs(var) in ignore, offset)
        for var in var_list
    ]


def construct_miter(outputs1: list[int], outputs2: list[int], max_var_num: int) -> list[list[int]]:
    result = []

    united_outputs_start = max_var_num
    for var1, var2 in zip(outputs1, outputs2):
        result.extend(xor_cnf(var1, var2, max_var_num))
        max_var_num += 1

    result.append(list(range(united_outputs_start, max_var_num)))
    return result


def create_schemas_lec(s1: CNFSchema, s2: CNFSchema) -> CNF:
    if len(s1.outputs) != len(s2.outputs):
        raise ValueError('Schemas differ in outputs, no need to start LEC')
    # Пока не работает, если у схем входы по-разному пронумерованы
    if s1.inputs != s2.inputs:
        raise ValueError('Schemas differ in inputs, no need to start LEC')

    outputs2 = unite_variables(s1.cnf, s2.outputs, ignore=s2.inputs, offset=len(s2.inputs))
    miter = construct_miter(s1.outputs, outputs2, s1.cnf.nv + s2.cnf.nv + 1 - len(s1.inputs))

    united = CNF(
        from_clauses=s1.cnf.clauses + [
            unite_variables(s1.cnf, clause, ignore=s2.inputs, offset=len(s2.inputs))
            for clause in s2.cnf.clauses
        ] + miter
    )

    return united


def map_var(mapping: dict[int, int], var: int) -> int:
    if var > 0:
        return mapping[var]
    elif var < 0:
        return -mapping[-var]
    return 0


def shuffle_cnf(f: CNF) -> (CNF, dict[int, int]):
    new_var_numbers = list(range(1, f.nv + 1))
    random.shuffle(new_var_numbers)
    mapping = {
        var: new_var
        for var, new_var in zip(range(1, f.nv + 1), new_var_numbers)
    }
    new_clauses = [[map_var(mapping, var) for var in clause] for clause in f.clauses]

    return CNF(from_clauses=new_clauses), mapping


if __name__ == '__main__':
    formula = CNF(from_file='tests/cnf/example_formula.cnf')
    g = Glucose3(formula.clauses)
    print(precount_set_order(formula, g, level=3))
    print(var_frequency(formula))
    print(extremum_indices([1, 2, 3, 4, 5, 4, 6, 7, 8, 0]))


def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        taken_time = time.perf_counter() - start
        sys.stderr.write(f'Time: {round(taken_time, 3)} seconds\n')
        return result
    return wrapper
