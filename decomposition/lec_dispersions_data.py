import os

import numpy as np
from pysat.formula import CNF

from decomposition.lec import compare_inputs
from util.util import var_coeff

if __name__ == '__main__':
    path_to_lec = os.path.join('tests', 'lec')

    lec_instances = [(CNF(from_file=os.path.join(path_to_lec, lec_instance_file)),
                      lec_instance_file.replace('.cnf', ''))
                     for lec_instance_file in os.listdir(path_to_lec)]

    lec_instances.sort(key=lambda li: li[0].nv)

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
        vc_inp, vc_ans, vc_rnd = var_coeff(tms_inputs), var_coeff(tms_answer), var_coeff(tms_random)

        # коэффициент вариации, чтобы не зависеть от величины времени дисперсии
        if all(not np.isnan(x) for x in [vc_inp, vc_ans, vc_rnd]):
            print('Writing to file')
            with open('stats/lec2/covariance_stat_all.stat', 'a') as cov_total:
                cov_total.write(f'{vc_inp} {vc_ans} {vc_rnd}\n')
