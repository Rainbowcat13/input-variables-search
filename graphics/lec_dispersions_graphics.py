import os
import matplotlib.pyplot as plt


def cov_graphic(cov_ans, cov_random, cov_ideal=None, save_to=None, xs=None):
    x = list(range(1, len(cov_random) + 1))

    plt.figure(figsize=(24, 16), dpi=300)
    plt.ylabel('Величина коэффициента вариации', fontsize=40)
    plt.xlabel('Схемы', fontsize=40)
    plt.title(
        'Коэффициент вариации времён работы SAT-решателя\n для оценок подстановок входов на различных схемах',
        fontsize=40
    )

    plt.xticks(x, xs or [''] * len(cov_random), fontsize=25, rotation=45, ha='right')
    plt.yticks(fontsize=40)
    plt.grid(True)
    plt.plot(x, cov_random, marker='o', linestyle='-', linewidth=7.0, color='red', label='Случайное множество')
    plt.plot(x, cov_ans, marker='o', linestyle='-', linewidth=7.0, color='blue', label='Найденные входы')
    if cov_ideal is not None:
        plt.plot(x, cov_ideal, marker='o', linestyle='-', linewidth=7.0, color='green', label='Настоящие входы')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), ncol=2, fontsize=25)

    if save_to is not None:
        plt.savefig(save_to)
    else:
        plt.show()


if __name__ == '__main__':
    all_stats = open(os.path.join('stats', 'lec', 'covariance_stat_all.stat'), 'r')

    cov_ideal = []
    cov_random = []
    cov_ans = []

    for line in all_stats.readlines():
        i, a, r = [float(x) for x in line.strip().split()]
        cov_ideal.append(i)
        cov_ans.append(a)
        cov_random.append(r)

    cov_graphic(cov_ans, cov_random, cov_ideal, 'stats/dispersion_ratio_better.png')

    x = list(range(1, len(cov_random) + 1))
