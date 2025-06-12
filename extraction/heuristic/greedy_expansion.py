from __future__ import annotations

import random
import sys
from multiprocessing import Pool

from tqdm import tqdm

from pysat.formula import CNF
from pysat.solvers import Glucose3

from util.util import fitness, ConflictTolerance

ESTIMATION_VECTOR_COUNT = 100
POOL_SIZE = 8
POOL_CHUNK_SIZE = 50
random.seed(22)


def fitness_zero_tolerance(f, candidate_with_var, estimation_vector_count, conflict_tolerance):
    return fitness(f, candidate_with_var, estimation_vector_count, conflict_tolerance=conflict_tolerance)


def count_ratios(f: CNF, candidate: list[int], new_vars: list[int], estimation_vector_count: int,
                 pool: Pool | None, pool_chunk_size=None, conflict_tolerance=ConflictTolerance.NORMAL):
    if pool is not None:
        ratios = pool.starmap(fitness_zero_tolerance, [
            (
                f,
                candidate + [var],
                estimation_vector_count,
                conflict_tolerance
            ) for var in new_vars
        ], chunksize=pool_chunk_size or POOL_CHUNK_SIZE)
    else:
        solver = Glucose3(bootstrap_with=f.clauses)
        n = len(new_vars)
        ratios = [None for _ in range(n)]
        for i in range(n):
            candidate.append(new_vars[i])
            ratios[i] = fitness(solver, candidate, estimation_vector_count)
            candidate.pop()

    return ratios


def count_good_conflict_var(
        ratios: list[tuple[float, float]],
        new_vars: list[int],
        inverted: bool = False
) -> (int | None, float):
    choice = max if inverted else min
    idx, ratio = choice(enumerate(ratios), key=lambda rs: rs[1][1])
    return new_vars[idx], ratio[1]


def expand_one_step(f: CNF, candidate: list[int], sample_size=None,
                    estimation_vector_count=ESTIMATION_VECTOR_COUNT, pool=None) -> list[int]:
    if len(candidate) == f.nv:
        return candidate

    non_used = list(set(range(1, f.nv)) - set(candidate))

    new_vars = random.sample(non_used, sample_size) if sample_size is not None else non_used
    ratios = count_ratios(f, candidate, new_vars, estimation_vector_count, pool)
    min_conflict_var, _ = count_good_conflict_var(ratios, new_vars)

    if min_conflict_var is None:
        return candidate

    return candidate + [min_conflict_var]


def expand(
        f: CNF, pickle: list[int], size_upper_bound: int, sample_size=None, conflict_border=None,
        estimation_vector_count=ESTIMATION_VECTOR_COUNT, pool=None, break_on_decline=False,
        pool_chunk_size=None, show_progress_bar=True, conflict_tolerance=ConflictTolerance.NORMAL, inverted=False
) -> tuple[list[int], list[int]]:
    candidate = set(pickle)
    non_used = set(range(1, f.nv + 1)) - candidate
    prev_min_ratio = 1
    target = min(size_upper_bound, f.nv)

    pbar = None
    if show_progress_bar:
        pbar = tqdm(total=target - len(candidate), desc='Expanding candidate', leave=True, file=sys.stderr)

    max_prop_ratio = -1.1
    max_prop_cand = None
    while len(candidate) < target:
        cand_list = list(candidate)
        prop_ratio, _ = fitness(f, cand_list, estimation_vector_count, conflict_tolerance)
        if prop_ratio > max_prop_ratio:
            max_prop_ratio = prop_ratio
            max_prop_cand = cand_list + []

        new_vars = list(
            random.sample(list(non_used), sample_size)
            if sample_size is not None and sample_size < len(non_used)
            else non_used
        )
        ratios = count_ratios(f, cand_list, new_vars, estimation_vector_count,
                              pool=pool, pool_chunk_size=pool_chunk_size,
                              conflict_tolerance=conflict_tolerance)
        min_conflict_var, min_conflict_ratio = count_good_conflict_var(ratios, new_vars, inverted=inverted)

        if any([
            min_conflict_var is None,
            break_on_decline and prev_min_ratio < min_conflict_ratio,
            conflict_border is not None and conflict_border < min_conflict_ratio
        ]):
            break

        prev_min_ratio = min_conflict_ratio
        candidate.add(min_conflict_var)
        non_used.remove(min_conflict_var)
        if pbar is not None:
            pbar.update(1)

    if pbar is not None:
        pbar.close()

    return list(candidate), max_prop_cand
