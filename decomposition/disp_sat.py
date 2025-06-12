import os
import random
import sys

import numpy as np
from pysat.formula import CNF
from pysat.solvers import Cadical195
from tqdm import tqdm

from util.util import inputs_outputs, basename_noext, score, ScoreMethod, percents, \
    random_assumptions, timeit

ESTIMATION_VECTOR_COUNT = 1000


if __name__ == '__main__':
    sat2021_answers_dir = os.path.join('.', 'answers', 'sat2021')
    sat2021_answers = os.listdir(sat2021_answers_dir)

    for ans_file in sat2021_answers:
        formula_name = basename_noext(ans_file)
        fname_wout_id = formula_name.split('-')[1]

        formula = CNF(from_file=os.path.join('tests', 'sat2021', f'{formula_name}.cnf'))
        solver = Cadical195(formula)
        possible_inputs = inputs_outputs(os.path.join(sat2021_answers_dir, ans_file))

        pts_prop = score(formula, solver, possible_inputs, ESTIMATION_VECTOR_COUNT, ScoreMethod.PROP)
        pts_cfl = score(formula, solver, possible_inputs, ESTIMATION_VECTOR_COUNT, ScoreMethod.CONFLICTS)

        print(f'Formula: {formula_name}')
        print(f'Input set size (% from formula size): {percents(len(possible_inputs) / formula.nv)}%')
        print(f'Points propagation: {percents(pts_prop)}%')
        print(f'Conflicts ratio: {percents(-pts_cfl)}%')

        rnd_vars = random.sample(list(range(1, formula.nv + 1)), len(possible_inputs))
        assumptions_inp = random_assumptions(possible_inputs, num_assumptions=1000)
        assumptions_rnd = random_assumptions(rnd_vars, num_assumptions=1000)
        tms_inp = []
        tms_rnd = []
        for a in tqdm(assumptions_inp, desc='Assumptions solved input', file=sys.stderr):
            timeit(callback_func=lambda tm: tms_inp.append(tm))(lambda: solver.solve(a))()
        for a in tqdm(assumptions_rnd, desc='Assumptions solved random', file=sys.stderr):
            timeit(callback_func=lambda tm: tms_rnd.append(tm))(lambda: solver.solve(a))()
        v_inp = np.var(tms_inp, ddof=1)
        v_rnd = np.var(tms_rnd, ddof=1)
        print(f'Variance possible input: {v_inp:.9f}')
        print(f'Variance random: {v_rnd:.9f}')
        print()
