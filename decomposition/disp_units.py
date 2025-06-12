import os
import random
import sys
from multiprocessing import freeze_support

import numpy as np
from pysat.formula import CNF
from pysat.solvers import Cadical195
from tqdm import tqdm
import matplotlib.pyplot as plt

from extraction.extractor import InputsExtractor, ExtractionMode
from util.util import remove_miter
from util.util import inputs_outputs, random_assumptions, timeit, basename_noext, extract_filenames, remove_zeroes

if __name__ == '__main__':
    # ex_files = list(filter(lambda file: basename_noext(file).startswith('ex'),
    #                        extract_filenames(['answers/extractor'], '.ans')))
    files = list(filter(lambda fn: 'unit' in fn, extract_filenames(['tests/inputs'], '.inputs')))
    stat_file = open('../stats/units_tm.stat', 'w')

    for example in files:
        example = basename_noext(example)
        print(example, file=stat_file)
        print(example)
        ans_file = os.path.join('../tests', 'inputs', f'{example}.inputs')
        cnf_file = os.path.join('../tests', 'lec', f'{example}.cnf')
        #
        formula = remove_zeroes(CNF(from_file=cnf_file))
        wout_miter, miter = remove_miter(formula)
        solver = Cadical195(formula)

        extractor = InputsExtractor(wout_miter)
        inputs = extractor.extract(mode=ExtractionMode.FAST)
        print('ABOBA')
        # print(*inputs)
        # with open(ans_file, 'w') as af:
        #     af.write(f'{len(inputs)}\n{" ".join(map(str, inputs))}\n')
        #
        # try:
        #     inputs = inputs_outputs(ans_file)
        # except Exception as e:
        #     print(e)
        #     continue
        print(len(inputs))
        rnd_vars = random.sample(list(range(1, formula.nv + 1)), len(inputs))

        print(inputs)
        print(rnd_vars)

        assumptions_inp = random_assumptions(inputs, num_assumptions=1000)
        assumptions_rnd = random_assumptions(rnd_vars, num_assumptions=1000)
        #
        tms_inp = []
        tms_rnd = []
        for a in tqdm(assumptions_inp, desc='Assumptions solved input', file=sys.stderr):
            timeit(callback_func=lambda tm: tms_inp.append(tm))(lambda: solver.solve(a))()
        for a in tqdm(assumptions_rnd, desc='Assumptions solved random', file=sys.stderr):
            timeit(callback_func=lambda tm: tms_rnd.append(tm))(lambda: solver.solve(a))()
        #
        print(*tms_inp, file=stat_file)
        print(*tms_rnd, file=stat_file)
        #
        v_inp = np.var(tms_inp, ddof=1)
        v_rnd = np.var(tms_rnd, ddof=1)
        print(v_inp, v_rnd)
        print(v_inp < v_rnd)

        data_inp = np.array(tms_inp)
        data_rnd = np.array(tms_rnd)

        np.random.shuffle(data_inp)
        np.random.shuffle(data_rnd)

        inp_mean = data_inp.mean()
        inp_std = data_inp.std(ddof=0)

        rnd_mean = data_rnd.mean()
        rnd_std = data_rnd.std(ddof=0)

        plt.cla()
        plt.clf()
        plt.figure(figsize=(24, 16), dpi=300)
        x = list(range(1, len(data_inp) + 1))

        plt.xticks(fontsize=40)
        plt.yticks(fontsize=40)
        plt.plot(x, data_inp, marker='o', linestyle='-', linewidth=1.5, label='Дисперсия на входах', color='green')
        plt.axhline(inp_mean, color='cyan', linestyle='--', linewidth=1.2,
                    label=f'Среднее дисперсии на входах = {inp_mean:.8f}')
        plt.fill_between(x, inp_mean - inp_std, inp_mean + inp_std,
                         color='lightgreen', alpha=0.1,
                         label=f'Зона ±1σ для входов ({inp_std:.8f})')

        plt.plot(x, data_rnd, marker='o', linestyle='-', linewidth=1.5, label='Дисперсия на случайном мн-ве',
                 color='red')
        plt.axhline(rnd_mean, color='brown', linestyle='--', linewidth=1.2,
                    label=f'Среднее дисперсии на случайном мн-ве = {inp_mean:.8f}')
        plt.fill_between(x, rnd_mean - rnd_std, rnd_mean + rnd_std,
                         color='lightcoral', alpha=0.1,
                         label=f'Зона ±1σ для случайного мн-ва ({rnd_std:.8f})')

        plt.xlabel('Подстановки', fontsize=40)
        plt.ylabel('Отнормированное время работы на подстановке', fontsize=40)
        plt.title('Дисперсия времени работы SAT-решателя\nна входах и на случайных подстановках', fontsize=40)
        plt.yscale('log')
        # plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), ncol=6, fontsize=25)
        plt.legend(fontsize=25)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f'graphics/disp_pics/{example}_{example}.png')

