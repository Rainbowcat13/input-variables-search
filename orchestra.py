import random
import sys
from multiprocessing import Pool, freeze_support

from pysat.formula import CNF
from pysat.solvers import Glucose3

from greedy_expansion import expand
from evolution import evolution, evolution_arg_parser
from util import fitness


def create_evolution_params(set_size):
    return evolution_arg_parser.parse_args(
        [
            'pupa',
            '-s', str(set_size),
            '-e', '120',
            '-g', '10000',
            '-r', '13',
        ]
    )


upper_bounds = sum([[2 ** x] * 2 for x in range(3, 9)], [])
RANDOM_SAMPLES_COUNT = len(upper_bounds)

if __name__ == '__main__':
    freeze_support()
    formula_filename = 'formula.cnf'
    if len(sys.argv) > 1:
        formula_filename = sys.argv[1]

    random.seed(13)

    formula = CNF(from_file=formula_filename)
    g = Glucose3(formula.clauses)

    expansion_pool_args = [
        (
            CNF(from_clauses=formula.clauses),
            var,
            upper_bound
        )
        for var, upper_bound in zip(
            random.sample(range(1, formula.nv), RANDOM_SAMPLES_COUNT),
            # list(range(1, formula.nv)),
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

    sys.stderr.write('Expansion stage results...\n')
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
    for result in results:
        prop_ratio, conflict_ratio = fitness(g, result[0], 1000)
        print(f'Propagation ratio: {prop_ratio}. Conflict ratio: {conflict_ratio}')
        print(len(result[0]))
        print(*sorted(result[0]))
