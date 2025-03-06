import random

from pysat.formula import CNF
from pysat.solvers import Glucose3


random.seed(13)

START_SIZE = 3
POPULATION_SIZE = 100
ESTIMATION_VECTORS_COUNT = 1000
ELEMENT_MUTATION_RATE = 0.01
GENERATIONS_COUNT = 10

formula = CNF(from_file='formula.cnf')
number_vars = formula.nv
g = Glucose3(formula.clauses)


def start_population(f: CNF):
    return [[random.randint(1, f.nv) for _ in range(START_SIZE)] for _ in range(POPULATION_SIZE)]


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
    for j in range(len(res)):
        if random.random() < ELEMENT_MUTATION_RATE:
            x = random.randint(1, f.nv)
            while x in res:
                x = random.randint(1, f.nv)
            res[j] = x
    return res


population = start_population(formula)
for gen in range(GENERATIONS_COUNT):
    print(f'Generation {gen + 1}/{GENERATIONS_COUNT}')
    offspring = [mutate(formula, candidate) for candidate in population]

    for i in range(POPULATION_SIZE):
        anc_fit = fitness(formula, g, population[i])
        off_fit = fitness(formula, g, offspring[i])

        if anc_fit < off_fit:
            population[i] = offspring[i]

mx = -1
result = []
for candidate in population:
    score = fitness(formula, g, candidate)
    if score > mx:
        result = candidate + []

print(len(result))
print(*result)
