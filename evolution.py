import random
import argparse

from pysat.formula import CNF
from pysat.solvers import Glucose3

from util import fitness


evolution_arg_parser = argparse.ArgumentParser(
    prog='Evolution algorithm',
    description='Uses evolutionary algorithm to determine input variables of a logical schema in CNF'
)
evolution_arg_parser.add_argument('filename', type=str, help='.cnf filename to get function from', default='formula.cnf')
evolution_arg_parser.add_argument('-s', '--start-set-size', type=int, help='possible input start size', default=20)
evolution_arg_parser.add_argument('-p', '--population-size', type=int, help='population size', default=1)
evolution_arg_parser.add_argument('-e', '--estimation-vectors-count', type=int,
                                  help='number of probe propagations to determine how good is possible input', default=1000)
evolution_arg_parser.add_argument('-g', '--generations-count', type=int, help='generations number', default=1000)
evolution_arg_parser.add_argument('-r', '--random-seed', type=int, help='seed for random', default=1337)
evolution_arg_parser.add_argument('-m', '--mode', type=str, help='mode for', default='solve',
                                  choices=['solve', 'conflicts'])


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
    mut_rate = 1 / len(candidate)
    res = candidate + []
    mutated_indexes = []
    for j in range(len(res)):
        if random.random() < mut_rate:
            mutated_indexes.append(j)

    mut_set = set(range(1, f.nv)) - set(candidate)
    if not mut_set:
        return res

    for index in mutated_indexes:
        res[index] = random.choice(list(mut_set))
        mut_set.remove(res[index])

    return res


# if formula is given, ignores parsing CNF from file
# if population is give, uses it as a start
def evolution(params, formula=None, population=None):
    if formula is None:
        formula = CNF(from_file=params.filename)
    if population is None:
        population = start_population(formula)

    g = Glucose3(formula.clauses)
    best = population[0]
    fit_best = fitness(g, best, params.estimation_vectors_count)[0]
    conflicts_ratio_sum = 0
    for gen in range(params.generations_count):
        # sys.stderr.write(f'Generation {gen + 1}/{params.generations_count}\n')
        offspring = [mutate(formula, candidate) for candidate in population]

        for i in range(params.population_size):
            off_fit, conflicts_ratio = fitness(g, offspring[i], params.estimation_vectors_count)
            conflicts_ratio_sum += conflicts_ratio
            if off_fit >= fit_best:
                best = offspring[i]
                fit_best = off_fit
                population[i] = offspring[i]

    mx = (-1, -1)
    result = []
    for candidate in population:
        score = fitness(g, candidate, params.estimation_vectors_count)
        if score[0] > mx[0]:
            result = candidate + []
            mx = score

    return result, conflicts_ratio_sum


if __name__ == '__main__':
    parameters = evolution_arg_parser.parse_args()
    random.seed(parameters.random_seed)
    result, conflicts_ratio_sum = evolution(parameters)

    if parameters.mode == 'solve':
        print(len(result))
        print(*sorted(result))
    elif parameters.mode == 'conflicts':
        print(parameters.start_set_size, round(conflicts_ratio_sum / parameters.generations_count, 5), sep=': ')
