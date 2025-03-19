import random
import argparse

from pysat.formula import CNF
from pysat.solvers import Glucose3

from util import fitness


def start_population(f: CNF):
    return [
        [
            random.randint(1, f.nv)
            for _ in
            range(parameters.start_set_size)
        ]
        for _ in
        range(parameters.population_size)
    ]


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Evolution algorithm',
        description='Uses evolutionary algorithm to determine input variables of a logical schema in CNF'
    )
    parser.add_argument('filename', type=str, help='.cnf filename to get function from', default='formula.cnf')
    parser.add_argument('-s', '--start-set-size', type=int, help='possible input start size', default=20)
    parser.add_argument('-p', '--population-size', type=int, help='population size', default=1)
    parser.add_argument('-e', '--estimation-vectors-count', type=int,
                        help='number of probe propagations to determine how good is possible input', default=1000)
    parser.add_argument('-g', '--generations-count', type=int, help='generations number', default=1000)
    parser.add_argument('-r', '--random-seed', type=int, help='seed for random', default=1337)
    parser.add_argument('-m', '--mode', type=str, help='mode for', default='solve',
                        choices=['solve', 'conflicts'])

    parameters = parser.parse_args()

    random.seed(parameters.random_seed)
    ELEMENT_MUTATION_RATE = 1 / parameters.start_set_size

    formula = CNF(from_file=parameters.filename)
    number_vars = formula.nv
    g = Glucose3(formula.clauses)

    population = start_population(formula)
    best = population[0]
    fit_best = fitness(g, best, parameters.estimation_vectors_count)[0]
    conflicts_ratio_sum = 0
    for gen in range(parameters.generations_count):
        # print(f'Generation {gen + 1}/{parameters.generations_count}')
        offspring = [mutate(formula, candidate) for candidate in population]

        for i in range(parameters.population_size):
            off_fit, conflicts_ratio = fitness(g, offspring[i], parameters.estimation_vectors_count)
            conflicts_ratio_sum += conflicts_ratio
            if off_fit >= fit_best:
                best = offspring[i]
                fit_best = off_fit
                population[i] = offspring[i]

    mx = (-1, -1)
    result = []
    for candidate in population:
        score = fitness(g, candidate, parameters.estimation_vectors_count)
        if score[0] > mx[0]:
            result = candidate + []
            mx = score

    if parameters.mode == 'solve':
        print(len(result))
        print(*sorted(result))
    elif parameters.mode == 'conflicts':
        print(parameters.start_set_size, round(conflicts_ratio_sum / parameters.generations_count, 5), sep=': ')
