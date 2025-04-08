import random
import sys
from multiprocessing import Pool

from pysat.formula import CNF
from pysat.solvers import Glucose3

from util import fitness

ESTIMATION_VECTOR_COUNT = 100
RANDOM_SAMPLE_SIZE = 100
POOL_SIZE = 16
eps = 0.01


def expand(f: CNF, pickle, size_upper_bound: int, conflict_border=None) -> list[int]:
    solver = Glucose3(f.clauses)
    candidate = set(pickle)
    non_used = set(range(1, f.nv)) - candidate
    sys.stderr.write(f'Start length {len(pickle)}\n')
    while len(candidate) < min(size_upper_bound, f.nv):
        sys.stderr.write(f'Size {len(candidate)}\n')
        min_conflict_ratio = 1.01
        max_prop_ratio = 0
        min_conflict_var = None

        new_vars = random.sample(non_used, RANDOM_SAMPLE_SIZE)
        with Pool(POOL_SIZE) as pool:
            ratios = pool.starmap(fitness, [
                (
                    f,
                    list(candidate) + [var],
                    ESTIMATION_VECTOR_COUNT
                ) for var in new_vars
            ])

        for idx, ratio in enumerate(ratios):
            prop_ratio, conflict_ratio = ratio
            if conflict_ratio < min_conflict_ratio:
                # (abs(conflict_ratio - min_conflict_ratio) < eps and prop_ratio > max_prop_ratio)):
                min_conflict_var = new_vars[idx]
                min_conflict_ratio = conflict_ratio
                max_prop_ratio = prop_ratio
        # for new_var in random.sample(non_used, RANDOM_SAMPLE_SIZE):
        #     new_cand = list(candidate) + [new_var]
        #     prop_ratio, conflict_ratio = fitness(solver, new_cand, ESTIMATION_VECTOR_COUNT)
        #     if conflict_ratio < min_conflict_ratio:
        #         # (abs(conflict_ratio - min_conflict_ratio) < eps and prop_ratio > max_prop_ratio)):
        #         min_conflict_var = new_var
        #         min_conflict_ratio = conflict_ratio
        #         max_prop_ratio = prop_ratio

        if min_conflict_var is None:
            break
        if conflict_border is not None and min_conflict_ratio > conflict_border:
            break

        candidate.add(min_conflict_var)
        non_used.remove(min_conflict_var)

    return list(candidate)
