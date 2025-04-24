import random
import sys
import time
from multiprocessing import freeze_support, Pool

import numpy as np
from pysat.formula import CNF
from pysat.solvers import Glucose3

from tqdm import tqdm
import psutil

from extraction.config import Config
from extraction.heuristic.cut_conflicts import cut
from extraction.heuristic.greedy_expansion import expand
from util.util import score, ScoreMethod
from extraction.heuristic.evolution import create_evolution_params, evolution


pool_size = psutil.cpu_count(logical=False)


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


def find_inputs(f: CNF, config: Config) -> list[int]:
    random.seed(config.random_seed)
    np.random.seed(config.random_seed)

    expansion_sample_size = min(config.expansion_sample_size, f.nv)

    solver = Glucose3(bootstrap_with=f.clauses)
    # Расширяемся от некоторой выборки переменных на небольшой вход-кандидат, чтобы взять старт получше
    start_sets = [[x] for x in random.sample(range(1, formula.nv + 1), expansion_sample_size)]

    pool = None if not config.use_pool else Pool(pool_size)

    if config.use_pool:
        start_sets = list(tqdm(
            pool.imap_unordered(
                expand_unpacked,
                [((
                      formula,
                      start_set,
                      config.expansion_start_size
                  ), {'show_progress_bar': False}) for start_set in start_sets]
            ), total=expansion_sample_size, desc='First small expanding', file=sys.stderr))
    else:
        start_sets = list(tqdm(
            [expand(f, start_set, config.expansion_start_size, show_progress_bar=False) for start_set in start_sets],
            total=expansion_sample_size, desc='First small expanding', file=sys.stderr
        ))

    total_ratios = [(score(formula, solver, st[0], config.estimation_vector_count, config.score_method), i)
                    for i, st in enumerate(start_sets)]
    total_ratios.sort(key=lambda ratio_num: -ratio_num[0])
    # Выбираем несколько лучших небольших множеств
    best = [(start_sets[i], tr) for tr, i in total_ratios[:config.expansion_candidates_count]]

    expanded_sets = [expand_unpacked((
        (
            formula,
            st[0],
            config.input_size_upper_bound
        ),
        {
            'break_on_decline': config.break_on_decline,
            'sample_size': None if config.big_expansion_no_sample else expansion_sample_size,
            'pool': pool if config.use_pool else None,
            'pool_chunk_size': (
                                   formula.nv
                                   if config.big_expansion_no_sample
                                   else expansion_sample_size
                               ) // pool_size,
            'zero_conflict_tolerance': config.zero_conflict_tolerance,
            'conflict_border': config.expansion_conflict_border
        })
    ) for st, _ in best]

    final_candidates = []
    for i, st in enumerate(expanded_sets):
        # Первый – результат полного расширения, второй – лучший результат
        for j in range(2):
            current_cand = st[j]
            params = create_evolution_params(len(current_cand),
                                             generations=config.evolution_generations_count,
                                             estimation_vector_count=config.estimation_vector_count)

            evoluted, ratio_sum = evolution(params, formula, [current_cand])
            final_candidates.append(evoluted)

    for i in range(len(final_candidates)):
        conflict_ratio = -score(formula, solver, final_candidates[i], config.estimation_vector_count, ScoreMethod.CONFLICTS)
        with tqdm(desc=f'Candidate {i} cut iterations', leave=False, file=sys.stderr) as pbar:
            it = 0
            while conflict_ratio > config.cut_conflict_border and it < config.cut_iterations_count:
                final_candidates[i] = cut(formula, final_candidates[i], config.estimation_vector_count)
                conflict_ratio = -score(formula, solver, final_candidates[i],
                                        config.estimation_vector_count, ScoreMethod.CONFLICTS)
                pbar.update(1)
                it += 1

    best, pts_best = choose_best(formula, solver, final_candidates, config.estimation_vector_count, ScoreMethod.TOTAL)
    sys.stderr.write(f'Score: {round(pts_best, 5)}\n')

    return best


default_config = Config()


if __name__ == '__main__':
    freeze_support()

    formula_filename = 'tests/cnf/example_formula.cnf'
    if len(sys.argv) > 1:
        formula_filename = sys.argv[1]

    formula = CNF(from_file=formula_filename)
    inputs = find_inputs(formula, default_config)

    print(len(inputs))
    print(inputs)
