import random
import sys

from pysat.formula import CNF
from pysat.solvers import Glucose3


random.seed(13)

START_SET_SIZE = 15
POPULATION_SIZE = 1
ESTIMATION_VECTORS_COUNT = 1000
ELEMENT_MUTATION_RATE = 1 / START_SET_SIZE
GENERATIONS_COUNT = 1000

formula_filename = 'formula.cnf'
if len(sys.argv) > 1:
    formula_filename = sys.argv[1]

formula = CNF(from_file=formula_filename)
number_vars = formula.nv
g = Glucose3(formula.clauses)


def start_population(f: CNF):
    return [[random.randint(1, f.nv) for _ in range(START_SET_SIZE)] for _ in range(POPULATION_SIZE)]


def fitness(f: CNF, solver: Glucose3, candidate: list[int]) -> int:
    vectors = [candidate + [] for _ in range(ESTIMATION_VECTORS_COUNT)]
    for vector in vectors:
        for i in range(len(vector)):
            if random.random() < 0.5:
                vector[i] *= -1

    metric = 0
    for vector in vectors:
        no_conflicts, result = solver.propagate(vector)

        if not no_conflicts:
            return -1

        metric += len(result)

    return metric


def mutate(f: CNF, candidate: list[int]):
    res = candidate + []
    mutated_indexes = []
    for j in range(len(res)):
        if random.random() < ELEMENT_MUTATION_RATE:
            mutated_indexes.append(j)

    mut_set = set(range(1, f.nv)) - set(candidate)
    for index in mutated_indexes:
        res[index] = random.choice(list(mut_set))
        mut_set.remove(res[index])

    return res


population = start_population(formula)
best = population[0]
fit_best = fitness(formula, g, best)
for gen in range(GENERATIONS_COUNT):
    print(f'Generation {gen + 1}/{GENERATIONS_COUNT}')
    offspring = [mutate(formula, candidate) for candidate in population]

    for i in range(POPULATION_SIZE):
        off_fit = fitness(formula, g, offspring[i])

        if off_fit >= fit_best:
            best = offspring[i]
            fit_best = off_fit
            population[i] = offspring[i]

mx = -1
result = []
for candidate in population:
    score = fitness(formula, g, candidate)
    if score > mx:
        result = candidate + []

print(len(result))
print(*sorted(result))
