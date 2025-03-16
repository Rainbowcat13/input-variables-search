import os

import matplotlib.pyplot as plt

for file in os.listdir('stats/evolution'):
    with open(os.path.join('stats/evolution', file), 'r') as stat_file:
        ratios = [float(line.strip().split()[1]) for line in stat_file.readlines()]
        xs = list(range(1, len(ratios) + 1))
        plt.plot(xs, ratios)
        plt.savefig(f'stats/evolution/{file.replace(".stat", ".png")}')
        print(f'Saved png {file}')
        plt.clf()
