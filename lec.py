import sys

from pysat.formula import CNF
from pysat.solvers import Glucose3
from scipy import stats
from tqdm import tqdm

from extraction.extractor import InputsExtractor
from util.util import random_assumptions, xor_cnf, CNFSchema, create_schemas_lec, timeit, remove_zeroes, inputs_outputs

TASKS_COUNT = 200


def extract_inputs(lec_instance: CNF):
    return InputsExtractor(lec_instance).extract()


def remove_miter(lec_instance: CNF) -> (CNF, list[int]):
    miter = max(lec_instance.clauses, key=lambda clause: len(clause))
    (new_clauses := lec_instance.clauses + []).remove(miter)
    return CNF(from_clauses=new_clauses), miter


def construct_lambdas(inputs: list[int], max_var_num: int) -> (list[list[int]], list[int]):
    lambdas = []
    lambdas_outputs = []
    n = len(inputs)
    for i in range(0, n - 1, 2):
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


def estimation(lec_instance: CNF):
    lec_without_miter, miter = remove_miter(lec_instance)
    inputs = extract_inputs(lec_without_miter)
    print(inputs)

    time_estimations = estimate_lec(lec_instance, inputs)

    dsc = stats.describe(time_estimations, ddof=1)
    sys.stderr.write(f'Dispersion: {dsc.variance:.9f}\n')

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

    lec = remove_zeroes(CNF(from_file='tests/lec/unit10.cnf'))

    estimation(lec)
