import random
import sys

from pysat.formula import CNF
from pysat.solvers import Glucose3

from util import fitness

SIZE_UPPER_BOUND = 100
ESTIMATION_VECTOR_COUNT = 100


formula_filename = 'formula.cnf'
if len(sys.argv) > 1:
    formula_filename = sys.argv[1]

random.seed(13)

formula = CNF(from_file=formula_filename)
g = Glucose3(formula.clauses)

for start in range(1, formula.nv):
    candidate = {start}
    non_used = set(range(1, formula.nv)) - candidate
    while len(candidate) < SIZE_UPPER_BOUND:
        min_conflict_ratio = 1.01
        min_conflict_var = None

        for new_var in non_used:
            new_cand = list(candidate) + [new_var]
            prop_ratio, conflict_ratio = fitness(g, new_cand, ESTIMATION_VECTOR_COUNT)
            if conflict_ratio < min_conflict_ratio:
                min_conflict_var = new_var
                min_conflict_ratio = conflict_ratio

        candidate.add(min_conflict_var)
        non_used.remove(min_conflict_var)

    pr, cr = fitness(g, list(candidate), ESTIMATION_VECTOR_COUNT)
    print(pr, cr)
    print(list(candidate))
