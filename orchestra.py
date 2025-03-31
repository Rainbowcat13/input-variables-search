import random
import sys
from multiprocessing import Pool, freeze_support
import argparse

from pysat.formula import CNF
from pysat.solvers import Glucose3

from greedy_expansion import expand
from evolution import evolution, evolution_arg_parser
from util import fitness


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


def create_evolution_params(set_size):
    return evolution_arg_parser.parse_args(
        [
            'pupa',
            '-s', str(set_size),
            '-e', '120',
            '-g', '12000',
            '-r', '13',
        ]
    )


upper_bounds = sum([[2 ** x] for x in range(3, 9)], [])
RANDOM_SAMPLES_COUNT = len(upper_bounds)

if __name__ == '__main__':
    freeze_support()
    params = orchestra_arg_parser.parse_args()
    random.seed(params.random_seed)

    formula = CNF(from_file=params.filename)
    g = Glucose3(formula.clauses)

    expansion_pool_args = [
        (
            CNF(from_clauses=formula.clauses),
            var,
            upper_bound
        )
        for var, upper_bound in zip(
            random.sample(range(1, formula.nv), RANDOM_SAMPLES_COUNT),
            upper_bounds
        )
    ]

    sys.stderr.write('Starting expansion stage...\n')
    with Pool(RANDOM_SAMPLES_COUNT) as pool:
        evolution_candidates = pool.starmap(expand, expansion_pool_args)

    evolution_pool_args = [
        (
            create_evolution_params(len(candidate)),
            CNF(from_clauses=formula.clauses),
            [candidate]
        )
        for candidate in evolution_candidates
    ]

    if params.debug_info:
        print('Expansion stage results...')
        for result in evolution_candidates:
            prop_ratio, conflict_ratio = fitness(g, result, 1000)
            print(f'Propagation ratio: {prop_ratio}. Conflict ratio: {conflict_ratio}')
            print(len(result))
            print(*sorted(result))

    sys.stderr.write('Starting evolution stage...\n')
    with Pool(RANDOM_SAMPLES_COUNT) as pool:
        results = pool.starmap(evolution, evolution_pool_args)

    # Прикрутить третью стадию – отрезание конфликтов
    # Понять какой размер входа по графику роста конфликтов/пропагейтов
    # Возможно, бинпоиск?

    sys.stderr.write('Starting estimation stage...\n')

    if params.debug_info:
        for result in results:
            prop_ratio, conflict_ratio = fitness(g, result[0], 1000)
            print(f'Propagation ratio: {prop_ratio}. Conflict ratio: {conflict_ratio}')
            print(len(result[0]))
            print(*sorted(result[0]))

    best_prop, best_conflicts = None, None
    best_ratio_prop, best_ratio_conflicts = 0, 1.01
    for result in results:
        prop_ratio, conflict_ratio = fitness(g, result[0], 5000)
        if prop_ratio > best_ratio_prop:
            best_prop = result[0]
            best_ratio_prop = prop_ratio
        if conflict_ratio < best_ratio_conflicts:
            best_conflicts = result[0]
            best_ratio_conflicts = conflict_ratio

    if params.metric_mode == 'prop':
        print(len(best_prop))
        print(*sorted(best_prop))
    elif params.metric_mode == 'conflicts':
        print(len(best_conflicts))
        print(*sorted(best_conflicts))
