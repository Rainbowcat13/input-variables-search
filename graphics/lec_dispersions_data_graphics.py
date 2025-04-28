import os

import matplotlib.pyplot as plt
import numpy as np
from pysat.formula import CNF

import lec
from util.util import mkdirs, inputs_outputs

if __name__ == '__main__':
    path_to_lec = 'tests/lec'
    not_wanted = [
        "arbiter.cnf", "bar.cnf", "dec.cnf", "div.cnf", "hyp.cnf", "i2c.cnf",
        "int2float.cnf", "log2.cnf",
        "max.cnf", "multiplier.cnf", "priority.cnf", "router.cnf", "sin.cnf", "sqrt.cnf", "square.cnf",
        "voter.cnf"
    ]

    var_coeffs = []
    mkdirs('stats/lec')
    for lec_instance_file in os.listdir('tests/lec'):
        if lec_instance_file.split('_')[-1] in not_wanted:
            print('skip')
            continue
        nm = lec_instance_file.replace('.cnf', '')
        stat_file = os.path.join('stats/lec', nm + '_ideal.stat')
        lec_instance = CNF(from_file=os.path.join(path_to_lec, lec_instance_file))

        try:
            inputs = inputs_outputs(f'tests/inputs/{nm.split("_")[0]}.inputs')
        except:
            continue
        estimation = lec.estimation(lec_instance, inputs=inputs)

        with open(stat_file, 'w') as sf:
            sf.write(' '.join(map(str, estimation)))

        estimation = np.array(estimation, dtype=float)
        mu = estimation.mean()
        sigma = estimation.std(ddof=0)
        # коэффициент вариации, чтобы не зависеть от величины времени дисперсии
        var_coeffs.append(sigma / mu if mu != 0 else np.nan)

    with open('stats/lec/cov_stat_total_random.stat', 'w') as cov_total:
        cov_total.write(' '.join(map(str, filter(lambda x: not np.isnan(x), var_coeffs))))
