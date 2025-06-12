import os
import random
import sys
from multiprocessing import freeze_support

import numpy as np
from pysat.formula import CNF
from pysat.solvers import Cadical195
from tqdm import tqdm

from util.util import inputs_outputs, random_assumptions, timeit, basename_noext

if __name__ == '__main__':
    freeze_support()
    sat2021_files = [(file, open(os.path.join('../tests/sat2021', file), 'r').readline().split()[2])
                     for file in os.listdir('../tests/sat2021')]
    sat2021_files = [sf for sf in sat2021_files if sf[1].isnumeric()]
    sat2021_files.sort(key=lambda f: int(f[1]))
    unsat2021_files = list(filter(lambda f: 'unsat' in f[0], sat2021_files))

    stat_file = open('../stats/sat2021_inputs.stat', 'w')
    for example in unsat2021_files:
        print(example)
        example = basename_noext(example[0])
        example = 'ba5451cace1bb09e2d36b9f34c19146e-ctl_4291_567_6_unsat_pre'
        ans_file = os.path.join('../answers', 'sat2021', f'{example}.ans')
        cnf_file = os.path.join('../tests/sat2021', f'{example}.cnf')

        formula = CNF(from_file=cnf_file)
        solver = Cadical195(formula)

        # extractor = InputsExtractor(formula)
        # inputs = extractor.extract(mode=ExtractionMode.NON_SCHEMA)
        # with open(ans_file, 'w') as af:
        #     af.write(f'{len(inputs)}\n{" ".join(map(str, inputs))}\n')

        inputs = inputs_outputs(ans_file)
        rnd_vars = random.sample(list(range(1, formula.nv + 1)), len(inputs))

        assumptions_inp = random_assumptions(inputs, num_assumptions=10000)
        assumptions_rnd = random_assumptions(rnd_vars, num_assumptions=10000)

        tms_inp = []
        tms_rnd = []
        for a in tqdm(assumptions_inp, desc='Assumptions solved input', file=sys.stderr):
            timeit(callback_func=lambda tm: tms_inp.append(tm))(lambda: solver.solve(a))()
        for a in tqdm(assumptions_rnd, desc='Assumptions solved random', file=sys.stderr):
            timeit(callback_func=lambda tm: tms_rnd.append(tm))(lambda: solver.solve(a))()

        print(tms_inp)
        print(tms_rnd)

        v_inp = np.var(tms_inp, ddof=1)
        v_rnd = np.var(tms_rnd, ddof=1)
        print(v_inp, v_rnd, file=stat_file)
        print(v_inp < v_rnd, file=stat_file)

        timeit()(lambda: print(solver.solve(), file=stat_file))()
        print(np.mean(tms_inp) * (2 ** len(inputs)), file=stat_file)
        print(np.mean(tms_rnd) * (2 ** len(inputs)), file=stat_file)
        break
