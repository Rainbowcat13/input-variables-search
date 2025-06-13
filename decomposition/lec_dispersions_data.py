import os

import numpy as np
from pysat.formula import CNF

from decomposition.lec import compare_inputs
from util.util import mkdirs


def var_coeff(tms):
    tms = np.array(tms, dtype=float)
    mu = tms.mean()
    sigma = tms.std(ddof=0)

    return sigma / mu if mu != 0 else np.nan


if __name__ == '__main__':
    path_to_lec = os.path.join('tests', 'lec')

    mkdirs('stats/lec2')

    lec_instances = [(CNF(from_file=os.path.join(path_to_lec, lec_instance_file)),
                      lec_instance_file.replace('.cnf', ''))
                     for lec_instance_file in os.listdir(path_to_lec)]

    lec_instances.sort(key=lambda li: li[0].nv)

    var_coeffs = []
    for lec_instance, schema_name in lec_instances:
        schema_subname = schema_name.split('_')[0]
        if 'unit' in schema_subname:
            continue
        print(schema_subname)

        inp_file = os.path.join('tests', 'inputs', f'{schema_subname}.inputs')
        ans_file = os.path.join('answers', 'extractor', f'{schema_subname}.ans')

        cmp = compare_inputs(lec_instance, inp_file, ans_file)
        if cmp is None:
            print('Damaged')
            continue
        tms_inputs, tms_answer, tms_random = cmp

        # коэффициент вариации, чтобы не зависеть от величины времени дисперсии
        var_coeffs.append((var_coeff(tms_inputs), var_coeff(tms_answer), var_coeff(tms_random)))

    var_coeffs_filtered = list(filter(lambda x: all(not np.isnan(y) for y in x), var_coeffs))

    print(var_coeffs_filtered)
    with open('stats/lec/covariance_stat_all.stat', 'w') as cov_total:
        cov_total.write('\n'.join(
            f'{x[0]} {x[1]} {x[2]}' for x in var_coeffs_filtered
        ))
