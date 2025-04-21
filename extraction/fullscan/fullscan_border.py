import sys
from itertools import combinations

from pysat.formula import CNF
from pysat.solvers import Glucose3

from util.util import fullscan_values


prop_cnt = 0


def find_inputs(formula: CNF) -> list[int]:
    number_vars = formula.nv
    solver = Glucose3(formula.clauses)
    global prop_cnt

    for count in range(1, number_vars):
        assumptions = list(combinations(range(1, number_vars + 1), count))
        for assumption in assumptions:
            for assumption_with_signs in fullscan_values(assumption, count):
                prop_cnt += 1
                no_conflicts, result = solver.propagate(assumption_with_signs)
                if not no_conflicts or len(result) != number_vars:
                    break
            else:
                return assumption

    return [i + 1 for i in range(number_vars)]


if __name__ == '__main__':
    formula_filename = 'tests/cnf/example_formula.cnf'
    if len(sys.argv) > 1:
        formula_filename = sys.argv[1]

    f = CNF(from_file=formula_filename)
    inputs = find_inputs(f)

    print(len(inputs))
    print(*sorted(inputs))
    sys.stderr.write(f'Complexity: {prop_cnt}\n')
