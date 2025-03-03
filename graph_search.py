import heapq

from pysat.formula import CNF
from pysat.solvers import Glucose3

from util import assumption_key

# Идея не работает и непонятно как сделать чтобы работала


def find_start_point(formula: CNF, solver: Glucose3):
    start_point = None
    output = None
    for var in range(1, formula.nv + 1):
        no_conflict_pos, output_pos = solver.propagate([var])
        no_conflict_neg, output_neg = solver.propagate([-var])
        if not no_conflict_pos or not no_conflict_neg:
            continue
        output_pos = set(assumption_key(output_pos))
        output_neg = set(assumption_key(output_neg))
        output_sum = output_pos.intersection(output_neg)
        if output is None or len(output_sum) > len(output[0].intersection(output[1])):
            output = (output_pos, output_neg)
            start_point = var

    return start_point, output


def dijkstra_with_border(
        formula: CNF,
        solver: Glucose3,
        start_var: int,
        start_output: tuple[set[int], set[int]],
        border: int
) -> list[tuple[int, list[int], set[int]]]:
    q = []
    dist = [(-1, [], {i}) for i in range(2 * formula.nv + 1)]
    dist[start_var] = (-len(start_output[0]), [start_var], start_output[0])
    dist[-start_var] = (-len(start_output[1]), [-start_var], start_output[1])
    heapq.heappush(q, (-len(start_output[0]), [start_var], start_output[0]))
    heapq.heappush(q, (-len(start_output[1]), [-start_var], start_output[1]))

    while q:
        power, variables, output = heapq.heappop(q)
        power *= -1
        if len(variables) == border:
            break
        # нужен множитель [-1, 1]
        # пропагейтить с известными -/+ и в стартвар заложить
        for v in range(-formula.nv, formula.nv + 1):
            if v == 0:
                continue

            power_v, vars_v, output_v = dist[v]
            power_v *= -1
            variables.append(v)
            no_conflicts, new_output = solver.propagate(variables)
            if not no_conflicts:
                variables.pop()
                continue

            if power_v < len(new_output):
                dist[v] = (-len(new_output), variables.copy(), new_output.copy())
                heapq.heappush(q, (-len(new_output), variables.copy(), new_output.copy()))

            variables.pop()

    return dist


f = CNF(from_file='formula.cnf')
g = Glucose3(f.clauses)
start_pt, start_vars = find_start_point(f, g)
if start_pt is None:
    print('Not satisfiable at all')
    exit(1)

d = dijkstra_with_border(f, g, start_pt, start_vars, 4)
max_output = None
result_set = None
for pwr, vrs, out in d:
    max_output = max_output or out
    result = result_set or vrs
    if pwr > len(max_output):
        max_output = out
        result_set = vrs

print('Output:')
print(len(max_output))
print(*max_output)
print('Variables set:')
print(len(result_set))
print(*result_set)
