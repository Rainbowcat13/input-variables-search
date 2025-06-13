import random
import sys

import numpy as np
from pysat.formula import CNF
from pysat.solvers import Cadical195
from tqdm import tqdm

from util.util import random_assumptions, timeit, do_with_time_limit, construct_lambdas


class DecompositionEstimation:
    def __init__(self, formula: CNF, inputs: list[int], estimation_vector_count: int = 1000,
                 assumption_time_limit: int = 1):
        self.formula = formula
        self.inputs = inputs
        self.estimation_vector_count = estimation_vector_count
        self.assumption_time_limit = assumption_time_limit
        self.solver = Cadical195(self.formula)
        self.times_random = []
        self.times_inputs = []
        self.var_random = 0
        self.var_inputs = 0
        self.estimation_random = 0
        self.estimation_inputs = 0

    def compare_with_random(self, use_lambdas=False) -> bool:
        self.times_inputs, self.var_inputs, self.estimation_inputs = self.estimate(self.inputs, use_lambdas)
        self.times_random, self.var_random, self.estimation_random = self.estimate(
            random.sample(list(range(1, self.formula.nv + 1)), len(self.inputs)),
            use_lambdas
        )
        return self.var_inputs < self.var_random

    def estimate(self, variables: list[int], use_lambdas=False) -> (list[float], int, int):
        est_vars = variables + []
        solver = self.solver
        if use_lambdas:
            lambdas, outputs = construct_lambdas(variables, self.formula.nv + 1)
            est_vars = outputs
            solver = Cadical195(bootstrap_with=CNF(from_clauses=self.formula.clauses + lambdas))

        tms = self._calc_times(est_vars, solver)
        return tms, np.var(tms), np.mean(tms) * (2 ** len(est_vars))

    def _calc_times(self, variables: list[int], solver=None) -> list[int]:
        if solver is None:
            solver = self.solver
        assumptions = random_assumptions(variables, num_assumptions=self.estimation_vector_count)
        result = []
        for a in tqdm(assumptions, desc='Assumptions solved', file=sys.stderr):
            timeit(
                callback_func=lambda tm: result.append(tm)
            )(
                lambda: do_with_time_limit(time_limit_seconds=self.assumption_time_limit)(solver.solve(a))()
            )()
        return result

    def print_stats(self, use_lambdas=False, file=None):
        print(f'Is variance better with inputs? {"Yes" if self.compare_with_random(use_lambdas) else "No"}',
              file=file, flush=True)
        print(f'Variance possible input: {self.var_inputs:.9f}', file=file, flush=True)
        print(f'Variance random: {self.var_random:.9f}', file=file, flush=True)
        print(f'Prediction possible input, seconds: {self.estimation_inputs:.9f}', file=file, flush=True)
        print(f'Prediction random, seconds: {self.estimation_random:.9f}', file=file, flush=True)
        print('Random times: ', file=file, flush=True)
        print(' '.join(map(str, self.times_random)), file=file, flush=True)
        print('Possible input times: ', file=file, flush=True)
        print(' '.join(map(str, self.times_inputs)), file=file, flush=True)
        print(file=file, flush=True)
        print('Written')
