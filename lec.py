import sys
import time

from pysat.formula import CNF
from pysat.solvers import Glucose3
from scipy import stats

from util import random_assumptions, xor_cnf, CNFSchema, create_schemas_lec

TASKS_COUNT = 1000


def extract_inputs(lec_instance: CNF) -> list[int]:
    # TODO: add extraction
    return []


def remove_miter(lec_instance: CNF) -> CNF:
    (new_clauses := lec_instance.clauses).remove(max(lec_instance.clauses, key=lambda clause: len(clause)))
    return CNF(from_clauses=new_clauses)


def construct_lambdas(inputs: list[int], max_var_num: int) -> (list[list[int]], list[int]):
    lambdas = []
    lambdas_outputs = []
    n = len(inputs)
    for i in range(0, n, 2):
        lambdas_outputs.append(max_var_num)
        lambdas.extend(xor_cnf(inputs[i], inputs[i + 1], max_var_num))
        max_var_num += 1
    if n % 2 == 1:
        lambdas_outputs.append(inputs[-1])

    return lambdas, lambdas_outputs


def estimate_lec(lec_instance: CNF, inputs: list[int]) -> list[float]:
    lec_without_miter = remove_miter(lec_instance)
    lambdas, new_inputs = construct_lambdas(inputs, lec_without_miter.nv + 1)

    lec_with_lambdas = CNF(from_clauses=lec_without_miter.clauses + lambdas)
    tasks = random_assumptions(new_inputs, TASKS_COUNT)
    solver = Glucose3(bootstrap_with=lec_with_lambdas.clauses)
    times = []

    for task in tasks:
        start = time.time()
        result = solver.solve(task)
        end = time.time()
        times.append(end - start)
        if not result:
            sys.stderr.write('UNSAT proved. Exiting.\n')
            break
    else:
        sys.stderr.write(f'Cannot find proof for UNSAT on {TASKS_COUNT} examples.\n')

    return times


def inputs_outputs(filename):
    with open(filename, 'r') as f:
        return [int(x) for x in f.readlines()[-1].strip().split()]


if __name__ == '__main__':
    adder = CNFSchema(
        CNF(from_file='tests/cnf/adder.cnf'),
        inputs_outputs('tests/inputs/adder.inputs'),
        inputs_outputs('tests/outputs/adder.outputs')
    )

    tms = estimate_lec(create_schemas_lec(adder, adder), adder.inputs)
    description = stats.describe(tms, ddof=1)
    print(f'Дисперсия задач: {description.variance:.9f}')
