import random
import sys
import time
from multiprocessing import Pool, freeze_support
import argparse

from pysat.formula import CNF
from pysat.solvers import Glucose3

from cut_conflicts import cut
from greedy_expansion import expand
from evolution import evolution, create_evolution_params
from util import fitness, precount_set_order, count_total_ratio

orchestra_arg_parser = argparse.ArgumentParser(
    prog='Orchestra of evolution and greedy algorithms',
    description='Uses orchestra of 2 algorithms to determine input variables of a logical schema in CNF'
)
orchestra_arg_parser.add_argument('filename', type=str, help='.cnf filename to get function from', default='formula.cnf')
orchestra_arg_parser.add_argument('-d', '--debug-info', type=bool, help='show debug info', default=False)
orchestra_arg_parser.add_argument('-r', '--random-seed', type=int, help='seed for random', default=1337)
orchestra_arg_parser.add_argument('-m', '--metric-mode', type=str,
                                  help='what metric to use to determine best result', choices=['prop', 'conflicts'],
                                  default='prop')


upper_bounds = [2 ** x for x in range(2, 9)] + [300]
RANDOM_SAMPLES_COUNT = len(upper_bounds)

if __name__ == '__main__':
    random.seed(1337)
    freeze_support()
    params = orchestra_arg_parser.parse_args()
    random.seed(params.random_seed)

    start_time = time.time()
    formula = CNF(from_file=params.filename)
    g = Glucose3(formula.clauses)
    CONFLICT_BORDER = 0.99
    START_SIZE = 15

    var_order = [lst[0] for lst in precount_set_order(formula, g, level=1)]
    var_sets = []
    evolution_candidates = []
    for start_var in [random.choice(list(range(1, formula.nv + 1)))]:
        cand_pickle = [start_var]
        for upper_bound in upper_bounds:
            current_result, _ = expand(formula, cand_pickle, upper_bound)
            if len(current_result) != upper_bound:
                if len(var_sets) > len(evolution_candidates):
                    evolution_candidates = var_sets + []
                var_sets = []
                break
            var_sets.append(current_result + [])
            cand_pickle = current_result + []
        else:
            break

    if len(var_sets) > len(evolution_candidates):
        evolution_candidates = var_sets + []
    evolution_pool_args = [
        (
            create_evolution_params(len(candidate)),
            CNF(from_clauses=formula.clauses),
            [candidate]
        )
        for candidate in evolution_candidates
    ]

    if params.debug_info:
        print('Expansion stage results:')
        for result in evolution_candidates:
            prop_ratio, conflict_ratio = fitness(g, result, 1000)
            print(f'Propagation ratio: {prop_ratio}. Conflict ratio: {conflict_ratio}')
            print(len(result))
            print(*sorted(result))

    sys.stderr.write('Starting evolution stage...\n')
    with Pool(RANDOM_SAMPLES_COUNT) as pool:
        cut_candidates = pool.starmap(evolution, evolution_pool_args)

    for result in cut_candidates:
        prop_ratio, conflict_ratio = fitness(g, result[0], 1000)
        print(f'Propagation ratio: {prop_ratio}. Conflict ratio: {conflict_ratio}')
        print(len(result[0]))
        print(*sorted(result[0]))

    sys.stderr.write('Starting cutting stage...\n')

    results = []
    for candidate in cut_candidates:
        print(len(candidate))
        total_ratio = count_total_ratio(formula, g, candidate[0], 100)

        cur_input = candidate[0] + []
        max_total = total_ratio
        best_input = cur_input + []
        while len(cur_input) > (len(results[-1]) if results else 1):
            old_length = len(cur_input)
            cur_input = cut(formula, cur_input, 100)

            cur_total = count_total_ratio(formula, g, cur_input, 100)
            if cur_total > max_total:
                max_total = cur_total
                best_input = cur_input + []

            if old_length == len(cur_input):
                break

        results.append(best_input)

    # Понять какой размер входа по графику роста конфликтов/пропагейтов
    # Возможно, бинпоиск?

    sys.stderr.write('Starting estimation stage...\n')

    if params.debug_info:
        for result in results:
            prop_ratio, conflict_ratio = fitness(g, result, 1000)
            print(f'Propagation ratio: {prop_ratio}. Conflict ratio: {conflict_ratio}')
            print(len(result))
            print(*sorted(result))

    # results = [x[0] for x in cut_candidates]
    best_prop, best_conflicts = None, None
    best_ratio_prop, best_ratio_conflicts = -1, 1.01
    for result in results:
        prop_ratio, conflict_ratio = fitness(g, result, 5000)
        if prop_ratio > best_ratio_prop:
            best_prop = result
            best_ratio_prop = prop_ratio
        if conflict_ratio < best_ratio_conflicts:
            best_conflicts = result
            best_ratio_conflicts = conflict_ratio

    if params.debug_info:
        print(f'prop: {best_ratio_prop}')
        print(len(best_prop))
        print(*sorted(best_prop))
        print(f'cfl: {best_ratio_conflicts}')
        print(len(best_conflicts))
        print(*sorted(best_conflicts))

    if params.metric_mode == 'prop':
        print(len(best_prop))
        print(*sorted(best_prop))
    elif params.metric_mode == 'conflicts':
        print(len(best_conflicts))
        print(*sorted(best_conflicts))

    sys.stderr.write(f'Completed in {round(time.time() - start_time, 3)} seconds.\n')
