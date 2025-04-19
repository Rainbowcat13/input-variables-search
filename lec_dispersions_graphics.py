import os

import matplotlib.pyplot as plt
import numpy as np
from pysat.formula import CNF

import lec
from util import mkdirs

if __name__ == '__main__':
    path_to_lec = 'tests/lec'
    wanted = [
        'div_div.cnf', 'multiplier_multiplier.cnf'
    ]

    estimations = []
    mkdirs('stats/lec')
    for lec_instance_file in wanted:
        stat_file = os.path.join('stats/lec', lec_instance_file.replace('.cnf', '.stat'))
        lec_instance = CNF(from_file=os.path.join(path_to_lec, lec_instance_file))
        estimation = lec.estimation(lec_instance)
        estimations.append(np.var(estimation, ddof=0))

        with open(stat_file, 'w') as sf:
            sf.write(' '.join(map(str, estimations)))

    plt.figure(figsize=(24, 16), dpi=300)
    plt.plot(wanted, estimations, marker='o', linestyle='-')
    # plt.bar(indices, variances)

    plt.xlabel('Номер инстанса')
    plt.ylabel('Дисперсия времени (сек²)')
    plt.title('Сравнение дисперсий времени работы по инстансам')
    plt.grid(True, which='both', ls='--', lw=0.5)
    plt.show()
