import random

import numpy as np
import matplotlib.pyplot as plt


POINTS_COUNT = 250


def cut_to_size(values: list[float], size: int) -> list[float]:
    if len(values) > size:
        return random.sample(values, size)
    return values


def prepare_data(arr, min_size):
    arr = cut_to_size(arr, min_size)
    arr = np.array(arr)
    np.random.shuffle(arr)
    return arr


def disp_graphic(data_inputs: list[float],
                 data_random: list[float],
                 save_to: str | None = None,
                 data_ideal: list[float] | None = None):
    min_size = min(
        len(data_inputs),
        len(data_random),
        len(data_ideal) if data_ideal is not None else len(data_inputs),
        POINTS_COUNT
    )

    inp = prepare_data(data_inputs, min_size)
    rnd = prepare_data(data_random, min_size)
    ideal = prepare_data(data_ideal, min_size) if data_ideal is not None else None

    inp_mean, inp_std = inp.mean(), inp.std(ddof=0)
    rnd_mean, rnd_std = rnd.mean(), rnd.std(ddof=0)

    plt.clf()
    plt.cla()
    plt.figure(figsize=(40, 24), dpi=300)
    x = list(range(1, len(inp) + 1))

    plt.xticks(fontsize=40)
    plt.yticks(fontsize=100)

    if ideal is not None:
        ideal_mean, ideal_std = ideal.mean(), ideal.std(ddof=0)
        plt.plot(x, ideal, marker='o', linestyle='-', linewidth=1.5,
                 label='Дисперсия на идеальном мн-ве', color='green')
        plt.axhline(ideal_mean, color='darkgreen', linestyle='--', linewidth=1.2,
                    label=f'Среднее идеального = {ideal_mean:.8f}')
        plt.fill_between(x, ideal_mean - ideal_std, ideal_mean + ideal_std,
                         color='lightgreen', alpha=0.1,
                         label=f'±1σ идеального ({ideal_std:.8f})')

        ci, li = 'blue', 'Дисперсия на входах'
        cm, ls = 'darkblue', 'Среднее входов'
        cf = 'lightblue'
    else:
        ci, li = 'green', 'Дисперсия на входах'
        cm, ls = 'cyan', 'Среднее входов'
        cf = 'lightgreen'

    plt.plot(x, inp, marker='o', linestyle='-', linewidth=1.5,
             label=li, color=ci)
    plt.axhline(inp_mean, color=cm, linestyle='--', linewidth=1.2,
                label=f'{ls} = {inp_mean:.8f}')
    plt.fill_between(x, inp_mean - inp_std, inp_mean + inp_std,
                     color=cf, alpha=0.1,
                     label=f'±1σ входов ({inp_std:.8f})')

    plt.plot(x, rnd, marker='o', linestyle='-', linewidth=1.5,
             label='Дисперсия на случайном мн-ве', color='red')
    plt.axhline(rnd_mean, color='darkred', linestyle='--', linewidth=1.2,
                label=f'Среднее случайного = {rnd_mean:.8f}')
    plt.fill_between(x, rnd_mean - rnd_std, rnd_mean + rnd_std,
                     color='lightcoral', alpha=0.1,
                     label=f'±1σ случайного ({rnd_std:.8f})')

    plt.xlabel('Подстановки', fontsize=40)
    plt.ylabel('Время работы на подстановке', fontsize=40)
    plt.title('Дисперсия времени работы SAT-решателя', fontsize=40)
    plt.yscale('log')
    plt.legend(fontsize=25)
    plt.grid(True)
    plt.tight_layout()

    if save_to:
        plt.savefig(save_to)
    else:
        plt.show()
