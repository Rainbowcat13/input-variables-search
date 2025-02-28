from pysat.formula import CNF
from pysat.solvers import Glucose3

import heapq


def find_start_point(formula: CNF, solver: Glucose3):
    start_point = None
    output = None
    for var in range(1, formula.nv + 1):
        conflict_pos, output_pos = solver.propagate([var])
        conflict_neg, output_neg = solver.propagate([-var])
        if conflict_pos or conflict_neg:
            continue
        output_sum = set(output_pos).intersection(set(output_neg))
        if len(output_sum) > len(output):
            output = output_sum
            start_point = var

    return start_point, output


def dijkstra_with_border(formula: CNF, solver: Glucose3, start_var: int, start_output: set[int], border: int):
    q = []
    dist = [(-1, 1, {i}) for i in range(formula.nv + 1)]
    dist[start_var] = (-len(start_output), 1, start_output)
    heapq.heappush(q, (-len(start_output), [start_var], start_output))
    while q:
        power, variables, output = heapq.heappop(q)
        power *= -1
        # нужен множитель [-1, 1]
        # пропагейтить с известными -/+ и в стартвар заложить
        for v in range(1, formula.nv + 1):

            power_v, length_v, output_v = dist[v]
            variables.append(v)
            conflict, new_output = solver.propagate(variables)



f = CNF(from_file='formula.cnf')
g = Glucose3(f.clauses)
start = find_start_point(f, g)
if start is None:
    print('Not satisfiable at all')
    exit(1)


