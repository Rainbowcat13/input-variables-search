import random
import sys
import time
from multiprocessing import freeze_support, Pool

import numpy as np
from pysat.formula import CNF
from pysat.solvers import Glucose3

from tqdm import tqdm
import psutil

from extraction.heuristics.cut_conflicts import cut
from extraction.heuristics.greedy_expansion import expand
from util.util import score, ScoreMethod
from extraction.heuristics.evolution import create_evolution_params, evolution


# Попытаемся оценить, сколько элементов надо выбрать, чтобы попасть хотя бы в один вход
# Если принять, что размер входа достигает x=0.001-0.01 от размера формулы,
# n — размер сэмпла чтобы в него почти наверное попал один из входов (вероятность 0.999), то n оценивается как
# ln(1 - 0.999) / ln(1 - x). Это примерно 7/x, для маленьких схем x~0.01, для больших x~0.001,
# т. е. примерно 700 и 7000
# Будем оценивать схему как маленькую, если в ней меньше 10000 переменных, как большую иначе
# TODO запустить стат-скрипт и посчитать насколько оценка близка к реальности на примерах
# Запустил, насколько близка хз, ну вроде +- да, разве что для больших схем скорее все-таки меньше, чем 0.001 доля
def count_sample_size(f: CNF) -> int:
    if f.nv >= 10000:
        return 7000
    else:
        return min(f.nv, 700)


def count_start_size(f: CNF) -> int:
    if f.nv > 100_000:
        return 3
    elif f.nv > 10_000:
        return 4
    elif f.nv > 1000:
        return 5
    return 6


def expand_unpacked(args):
    pos_args, kw_args = args
    return expand(*pos_args, **kw_args)


def print_score(cands):
    for cand in cands:
        scr = score(formula, solver, cand, 1000, ScoreMethod.PROP)
        print(scr)
        print(len(cand))
        print(*sorted(cand))


def choose_best(f: CNF, g: Glucose3, candidates: list[list[int]],
                estimation_vector_cnt: int, score_method: ScoreMethod) -> tuple[list[int], float]:
    best_cand = None
    best_pts = -1.1
    for candidate in candidates:
        pts = score(f, g, candidate, estimation_vector_cnt, score_method)
        if best_cand is None or pts > best_pts:
            best_cand = candidate
            best_pts = pts

    return best_cand, best_pts


if __name__ == '__main__':
    freeze_support()
    random.seed(22)
    np.random.seed(22)

    formula_filename = '../../tests/cnf/example_formula.cnf'
    break_on_decline = False
    zero_conflict_tolerance = False
    conflict_border = 0.45
    estimation_vector_count = 1000
    big_expansion_no_sample = False

    if len(sys.argv) > 1:
        formula_filename = sys.argv[1]
    if len(sys.argv) > 2:
        if sys.argv[2] == '--fasten':
            break_on_decline = True
            zero_conflict_tolerance = True
            estimation_vector_count = 100
        elif sys.argv[2] == '--slow':
            big_expansion_no_sample = True

    formula = CNF(from_file=formula_filename)
    solver = Glucose3(bootstrap_with=formula.clauses)

    # Параметры
    ESTIMATION_VECTOR_COUNT = 200
    INPUT_SIZE_UPPER_BOUND = 1500
    EXPANSION_CANDIDATES_COUNT = 1

    pool_size = psutil.cpu_count(logical=False)
    start_size = count_start_size(formula)
    sample_size = count_sample_size(formula)
    # -----------------------------------------

    # Расширяемся от некоторой выборки переменных на небольшой вход-кандидат, чтобы взять старт получше
    tm = time.time()
    start_sets = [[x] for x in random.sample(range(1, formula.nv + 1), sample_size)]

    with Pool(pool_size) as pool:
        start_sets = list(tqdm(
            pool.imap_unordered(
                expand_unpacked,
                [((
                      formula,
                      start_set,
                      start_size
                  ), {'show_progress_bar': False}) for start_set in start_sets]
            ), total=sample_size, desc='First small expanding', file=sys.stderr))

    total_ratios = [(score(formula, solver, st[0], ESTIMATION_VECTOR_COUNT, ScoreMethod.TOTAL), i)
                    for i, st in enumerate(start_sets)]
    total_ratios.sort(key=lambda ratio_num: -ratio_num[0])
    # Выбираем несколько лучших небольших множеств
    # Пока одно
    best = [(start_sets[i], tr) for tr, i in total_ratios[:EXPANSION_CANDIDATES_COUNT]]
    # best = [([1, 2, 3], 0.01)]

    with Pool(pool_size) as pool:
        expanded_sets = [expand_unpacked((
            (
                formula,
                st[0],
                INPUT_SIZE_UPPER_BOUND
            ),
            {
                'break_on_decline': break_on_decline,
                'sample_size': None if big_expansion_no_sample else sample_size,
                'pool': pool,
                'pool_chunk_size': (formula.nv if big_expansion_no_sample else sample_size) // pool_size,
                'zero_conflict_tolerance': zero_conflict_tolerance,
                'conflict_border': conflict_border
            })
        ) for st, _ in best]

    final_candidates = []
    for i, st in enumerate(expanded_sets):
        # Первый – результат полного расширения, второй – лучший результат
        for j in range(2):
            current_cand = st[j]
            params = create_evolution_params(len(current_cand),
                                             generations=10000,
                                             estimation_vector_count=estimation_vector_count)

            evoluted, ratio_sum = evolution(params, formula, [current_cand])
            final_candidates.append(evoluted)

    for i in range(len(final_candidates)):
        conflict_ratio = -score(formula, solver, final_candidates[i], estimation_vector_count, ScoreMethod.CONFLICTS)
        with tqdm(desc=f'Candidate {i} cut iterations', leave=False, file=sys.stderr) as pbar:
            while conflict_ratio > 0:
                final_candidates[i] = cut(formula, final_candidates[i], estimation_vector_count)
                conflict_ratio = -score(formula, solver, final_candidates[i],
                                        estimation_vector_count, ScoreMethod.CONFLICTS)
                pbar.update(1)

    best, pts_best = choose_best(formula, solver, final_candidates, estimation_vector_count, ScoreMethod.TOTAL)

    print(len(best))
    print(*sorted(best))

    sys.stderr.write(f'Score: {round(pts_best, 5)}\n')
    sys.stderr.write(f'Time: {round(time.time() - tm, 5)}\n')
