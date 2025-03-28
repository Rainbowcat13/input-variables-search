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


SIZE_UPPER_BOUND = 50
SIZE_LOWER_BOUND = 30
ESTIMATION_VECTOR_SIZE = 10
TRY_COUNT = 100

conflicts_ratio = [[] for _ in range(TRY_COUNT)]
prop_ratio = [[] for _ in range(TRY_COUNT)]
results = [(0, 0, []) for _ in range(TRY_COUNT)]
randomshit = 0
unsat_cnt = 0
prop_cnt = 0
core_none = 0

g = Glucose3(bootstrap_with=formula.clauses)
c = Cadical195(bootstrap_with=formula.clauses)

# print(c.propagate([])[0])
# print(g.propagate([])[0])

print(c.solve())
print(g.solve())

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
            no_conflicts, result = Glucose3(formula.clauses).propagate(assumption)
            unsat = Glucose3(formula.clauses).propagate()[0]
            if unsat:
                unsat_cnt += 1
            prop_cnt += 1

            if not no_conflicts:
                s = Glucose3(formula.clauses)
                core = s.get_core()
                if core is None:
                    core = []
                    core_none += 1

                conflicts_count += 1
                for var in set(assumption_key(core)) & input_cand:
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
            if max_conflicts == -1:
                randomshit += 1
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
print(f'Min conflict ratio: {min_conflict_ratio} with input:')
print(*min_conflict_result)
print(f'Max prop ratio: {max_prop_ratio}/{formula.nv} with input:')
print(*max_prop_result)
print(f'Random shit: {randomshit}')
print(f'Unsat: {unsat_cnt}/{prop_cnt}')
print(f'Core none: {core_none}/{prop_cnt}')
