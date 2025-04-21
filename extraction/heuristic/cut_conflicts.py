import random
import sys
from collections import defaultdict

from pysat.formula import CNF
from pysat.solvers import Glucose3

from util.util import random_assumptions, fitness, assumption_key


def cut(f: CNF, candidate: list[int], estimation_vector_count: int) -> list[int]:
    vars_set = set(candidate + [])
    assumptions_count = min(2 ** len(vars_set), estimation_vector_count)
    assumptions = random_assumptions(list(vars_set), assumptions_count)

    conflicts_count = 0
    prop_count = 0
    var_cause_conflict = defaultdict(int)
    for assumption in assumptions:
        solver = Glucose3(bootstrap_with=f.clauses)
        no_conflicts, res = solver.propagate(assumption)

        if not no_conflicts:
            sat = solver.solve(assumption)
            if sat:
                sys.stderr.write('Propagate has conflicts, solver does not!\n')
            core = solver.get_core()
            conflicts_count += 1
            for var in set(assumption_key(core or [])) & vars_set:
                var_cause_conflict[var] += 1
        else:
            prop_count += len(res)

    max_conflicts = -1
    conflict_var = None
    for var, var_conflict_count in var_cause_conflict.items():
        if var_conflict_count > max_conflicts:
            conflict_var = var
            max_conflicts = var_conflict_count

    if conflict_var is not None:
        vars_set -= {conflict_var}

    return list(vars_set)


if __name__ == '__main__':
    formula_filename = 'tests/cnf/example_formula.cnf'
    if len(sys.argv) > 1:
        formula_filename = sys.argv[1]

    random.seed(13)
    formula = CNF(from_file=formula_filename)

    SIZE_UPPER_BOUND = 150
    SIZE_LOWER_BOUND = 75
    ESTIMATION_VECTOR_SIZE = 10
    TRY_COUNT = 10

    conflicts_ratio = [[] for _ in range(TRY_COUNT)]
    prop_ratio = [[] for _ in range(TRY_COUNT)]
    results = [(0, 0, []) for _ in range(TRY_COUNT)]

    for t in range(1, TRY_COUNT + 1):
        print(f'Try count {t}')
        input_cand = random.sample(range(1, formula.nv), SIZE_UPPER_BOUND)
        while (old_length := len(input_cand)) > SIZE_LOWER_BOUND:
            input_cand = cut(formula, input_cand, ESTIMATION_VECTOR_SIZE)
            if len(input_cand) == old_length:
                break

        ratio = fitness(Glucose3(formula.clauses), input_cand, ESTIMATION_VECTOR_SIZE)
        results[t - 1] = (ratio[0], ratio[1], input_cand)

    min_conflict_ratio = 1.2
    max_prop_ratio = -1
    min_conflict_result = None
    max_prop_result = None
    for result in results:
        if result[0] > max_prop_ratio:
            max_prop_result = result[2]
            max_prop_ratio = result[0]
        if result[1] < min_conflict_ratio:
            min_conflict_result = result[2]
            min_conflict_ratio = result[1]
    print(f'Min conflict ratio: {min_conflict_ratio} with input:')
    print(len(min_conflict_result))
    print(*sorted(min_conflict_result))
    print(f'Max prop ratio: {max_prop_ratio}/{formula.nv} with input:')
    print(len(max_prop_result))
    print(*sorted(max_prop_result))
