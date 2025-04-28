import os
import random

import matplotlib.pyplot as plt
import numpy as np
from pysat.formula import CNF

import lec
from util.util import mkdirs

if __name__ == '__main__':
    path_to_lec = 'stats/lec'

    var_coeffs = []
    schema_names = []
    files = os.listdir(path_to_lec)
    ans_files = list(sorted(filter(lambda file: 'random' not in file and 'ideal' not in file and 'ex' in file, files)))
    random_files = list(
        sorted(
            filter(
                lambda file: 'random' in file and
                             any(file.split('_')[0] in a for a in ans_files),
                files
            )
        )
    )
    ideal_files = list(
        sorted(
            filter(
                lambda file: 'ideal' in file and
                             any(file.split('_')[0] in a for a in ans_files),
                files
            )
        )
    )

    cfs_r_to_a = []
    cfs_a_to_i = []

    cov_ideal = []
    cov_random = []
    cov_ans = []
    cnt1 = 0
    cnt2 = 0
    mxcr = 0
    for lsf_ans, lsf_ideal, lsf_random in zip(
        ans_files, ideal_files, random_files
    ):
        lsf_ans = os.path.join(path_to_lec, lsf_ans)
        lsf_ideal = os.path.join(path_to_lec, lsf_ideal)
        lsf_random = os.path.join(path_to_lec, lsf_random)

        with open(lsf_ans, 'r') as f:
            estimation_ans = list(map(float, f.read().split()))
        with open(lsf_ideal, 'r') as f:
            estimation_ideal = list(map(float, f.read().split()))
        with open(lsf_random, 'r') as f:
            estimation_random = list(map(float, f.read().split()))

        # удаляем выбросы (херово удаляем, но пока так)
        estimation_ans = list(sorted(estimation_ans))[2:-2]
        estimation_ideal = list(sorted(estimation_ideal))[2:-2]
        estimation_random = list(sorted(estimation_random))[2:-2]

        min_len = min(len(estimation_random), len(estimation_ideal), len(estimation_ans))
        if min_len < 8:
            continue

        estimation_ans = np.array(random.sample(estimation_ans, min_len), dtype=float)
        estimation_random = np.array(random.sample(estimation_random, min_len), dtype=float)
        estimation_ideal = np.array(random.sample(estimation_ideal, min_len), dtype=float)

        v_ans = np.var(estimation_ans, ddof=0)
        v_random = np.var(estimation_random, ddof=0)
        v_ideal = np.var(estimation_ideal, ddof=0)

        cov_c_i = estimation_ideal.std(ddof=0) / estimation_ideal.mean()
        cov_c_a = estimation_ans.std(ddof=0) / estimation_ans.mean()
        cov_c_r = estimation_random.std(ddof=0) / estimation_random.mean()

        cov_ideal.append(cov_c_i)
        cov_ans.append(cov_c_a)
        cov_random.append(cov_c_r)
        if v_ans < v_random:
            print('yeah')
            cnt1 += 1
        elif v_ans == v_random:
            print('so-so')
        else:
            print('nah')
            cnt2 += 1
        criteria = v_random / v_ideal
        if criteria > mxcr and min_len > 100:
            mxcr = criteria
            print('here')
            print('[', ', '.join(map(str, estimation_ans)), ']')
            print('[', ', '.join(map(str, estimation_random)), ']')

        cfs_r_to_a.append(cov_c_r / cov_c_a)
        cfs_a_to_i.append(cov_c_a / cov_c_i)
        # if m_random > m_ans:
        # print(m_ans, m_random, m_ideal)
        # break
        # mu = estimation.mean()
        # sigma = estimation.std(ddof=0)
        # v = estimation.var(ddof=0)
        # # коэффициент вариации, чтобы не зависеть от величины времени дисперсии
        # if mu != 0:
        #     var_coeffs.append(sigma / mu)
        #     schema_names.append(lec_stat_file.split('_')[0])

    print(cnt1, cnt2)

    # mean_cv = np.mean(var_coeffs)
    # std_cv = np.std(var_coeffs, ddof=0)

    x = list(range(1, len(cfs_r_to_a) + 1))

    plt.figure(figsize=(24, 16), dpi=300)
    plt.ylabel('Величина коэффициента вариации', fontsize=40)
    plt.xlabel('Схемы', fontsize=40)
    plt.title('Коэффициент вариации\n для оценок подстановок входов на различных схемах', fontsize=40)

    plt.xticks(x, fontsize=40)
    plt.yticks(fontsize=40)
    plt.grid(True)
    plt.plot(x, cov_random, marker='o', linestyle='-', linewidth=7.0, color='red', label='Случайное множество')
    plt.plot(x, cov_ans, marker='o', linestyle='-', linewidth=7.0, color='green', label='Найденные входы')
    # plt.xticks(x, schema_names, rotation=45, fontsize=12)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), ncol=2, fontsize=25)
    plt.savefig(
        'stats/dispersion_ratio.png'
    )
