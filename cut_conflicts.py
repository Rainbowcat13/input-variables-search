import random
import sys
from collections import defaultdict

from pysat.formula import CNF
from pysat.solvers import Glucose3, Cadical195

from util import random_assumptions, fitness, assumption_key


formula_filename = 'formula.cnf'
if len(sys.argv) > 1:
    formula_filename = sys.argv[1]

random.seed(13)

formula = CNF(from_file=formula_filename)
# g = Glucose3(formula.clauses)
# c = Cadical195(bootstrap_with=formula.clauses)
# solver = c


SIZE_UPPER_BOUND = 270
SIZE_LOWER_BOUND = 150
ESTIMATION_VECTOR_SIZE = 10
TRY_COUNT = 100

conflicts_ratio = [[] for _ in range(TRY_COUNT)]
prop_ratio = [[] for _ in range(TRY_COUNT)]
results = [(0, 0, []) for _ in range(TRY_COUNT)]

g = Glucose3(bootstrap_with=formula.clauses)
c = Cadical195(bootstrap_with=formula.clauses)

for t in range(TRY_COUNT):
    print(f'Try count {t}')
    input_cand = set(random.sample(range(1, formula.nv), SIZE_UPPER_BOUND))

    while len(input_cand) >= SIZE_LOWER_BOUND:
        assumptions_count = min(2 ** len(input_cand), ESTIMATION_VECTOR_SIZE)
        assumptions = random_assumptions(list(input_cand), assumptions_count)

        conflicts_count = 0
        prop_count = 0
        var_cause_conflict = defaultdict(int)
        for assumption in assumptions:
            solver = Glucose3(bootstrap_with=formula.clauses)
            no_conflicts, result = solver.propagate(assumption)

            if not no_conflicts:
                sat = solver.solve(assumption)
                if sat:
                    sys.stderr.write('Propagate has conflicts, solver does not!\n')
                core = solver.get_core()
                conflicts_count += 1
                for var in set(assumption_key(core or [])) & input_cand:
                    var_cause_conflict[var] += 1
            else:
                prop_count += len(result)

        max_conflicts = -1
        conflict_var = random.choice(list(input_cand))
        for var, var_conflict_count in var_cause_conflict.items():
            if var_conflict_count > max_conflicts:
                conflict_var = var
                max_conflicts = var_conflict_count

        conflicts_ratio[t].append(conflicts_count / ESTIMATION_VECTOR_SIZE)
        prop_ratio[t].append(prop_count / ESTIMATION_VECTOR_SIZE)

        if len(input_cand) > SIZE_LOWER_BOUND:
            input_cand.remove(conflict_var)
        else:
            break

    input_cand = list(input_cand)
    ratio = fitness(Glucose3(formula.clauses), input_cand, ESTIMATION_VECTOR_SIZE)
    results[t] = (ratio[0], ratio[1], input_cand)

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
# print(f'Min conflict ratio: {min_conflict_ratio} with input:')
# print(*sorted(min_conflict_result))
# print(f'Max prop ratio: {max_prop_ratio}/{formula.nv} with input:')
print(len(max_prop_result))
print(*sorted(max_prop_result))
