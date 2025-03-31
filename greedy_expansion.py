import sys

from pysat.formula import CNF
from pysat.solvers import Glucose3

from util import fitness

ESTIMATION_VECTOR_COUNT = 120
eps = 0.01


def expand(f: CNF, start: int, size_upper_bound: int, from_pickle=None) -> list[int]:
    solver = Glucose3(f.clauses)
    candidate = {start}
    if from_pickle is not None:
        candidate = set(from_pickle)
    non_used = set(range(1, f.nv)) - candidate
    sys.stderr.write(f'Start {start}\n')
    while len(candidate) < min(size_upper_bound, f.nv):
        sys.stderr.write(f'Size {len(candidate)}\n')
        min_conflict_ratio = 1.01
        max_prop_ratio = 0
        min_conflict_var = None

        for new_var in non_used:
            new_cand = list(candidate) + [new_var]
            prop_ratio, conflict_ratio = fitness(solver, new_cand, ESTIMATION_VECTOR_COUNT)
            if conflict_ratio < min_conflict_ratio:
                # (abs(conflict_ratio - min_conflict_ratio) < eps and prop_ratio > max_prop_ratio)):
                min_conflict_var = new_var
                min_conflict_ratio = conflict_ratio
                max_prop_ratio = prop_ratio

        if min_conflict_var is None:
            break

        candidate.add(min_conflict_var)
        non_used.remove(min_conflict_var)

    return list(candidate)
