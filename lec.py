import sys

from pysat.formula import CNF
from pysat.solvers import Glucose3, Cadical195
from scipy import stats
from tqdm import tqdm

from util.util import random_assumptions, xor_cnf, CNFSchema, create_schemas_lec, timeit

TASKS_COUNT = 20


def extract_inputs(lec_instance: CNF):
    return list(range(1, 129))


def remove_miter(lec_instance: CNF) -> (CNF, list[int]):
    miter = max(lec_instance.clauses, key=lambda clause: len(clause))
    (new_clauses := lec_instance.clauses + []).remove(miter)
    return CNF(from_clauses=new_clauses), miter


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
    lambdas, new_inputs = construct_lambdas(inputs, lec_instance.nv + 1)

    lec_with_lambdas = CNF(from_clauses=lec_instance.clauses + lambdas)
    tasks = random_assumptions(new_inputs, TASKS_COUNT)
    solver = Glucose3(bootstrap_with=lec_with_lambdas.clauses)
    times = []

    for task in tqdm(tasks, desc='Checking assumptions', file=sys.stderr):
        result = timeit(callback_func=lambda tm: times.append(tm))(lambda: solver.solve(task))()
        if result:
            sys.stderr.write('SAT found. Exiting.\n')
            sys.stderr.write(f'Model: {solver.get_model()}')
            break
    else:
        sys.stderr.write(f'Cannot find SAT on {TASKS_COUNT} examples.\n')

    return times


def inputs_outputs(filename):
    with open(filename, 'r') as f:
        return [int(x) for x in f.readlines()[-1].strip().split()]


def estimation(lec_instance: CNF):
    lec_without_miter, miter = remove_miter(lec_instance)
    inputs = extract_inputs(lec_without_miter)

    time_estimations = estimate_lec(lec_instance, inputs)
    total_time_prediction = (sum(time_estimations) / TASKS_COUNT) * 2 ** (len(inputs) - 1)
    sys.stderr.write(f'Based on inputs SAT solving will take approximately {total_time_prediction} s.\n')
    return time_estimations


if __name__ == '__main__':
    adder = CNFSchema(
        CNF(from_file='tests/cnf/adder.cnf'),
        inputs_outputs('tests/inputs/adder.inputs'),
        inputs_outputs('tests/outputs/adder.outputs')
    )

    xor = CNFSchema(
        CNF(from_file='tests/cnf/xor_gate.cnf'),
        inputs_outputs('tests/inputs/xor_gate.inputs'),
        inputs_outputs('tests/outputs/xor_gate.outputs')
    )

    lec = create_schemas_lec(adder, adder)

    tms = estimate_lec(lec, adder.inputs)
    description = stats.describe(tms, ddof=1)
    print(f'Dispersion: {description.variance:.9f}')
