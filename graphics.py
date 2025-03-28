import os
import sys

import matplotlib.pyplot as plt


wanted_schemas = sys.argv[1:]
colormap = plt.get_cmap("tab10")
n_graphics = len(wanted_schemas)
colors = {
    schema: color
    for schema, color in zip(
        wanted_schemas,
        [
            colormap(i % 10)
            for i in range(n_graphics)
        ]
    )
}

plt.figure(figsize=(24, 16), dpi=300)
plt.xlabel('Количество переменных в стартовом множестве', fontsize=40)
plt.ylabel('Доля конфликтующих подстановок', fontsize=40)
plt.title('Скорость роста доли конфликтов\nот размера множества для некоторых схем', fontsize=40)

for file in os.listdir('stats/evolution'):
    with open(os.path.join('stats/evolution', file), 'r') as stat_file:
        schema_name = file.replace('.stat', '')
        if schema_name in wanted_schemas:
            ratios = [float(line.strip().split()[1]) for line in stat_file.readlines()]
            xs = list(range(1, len(ratios) + 1))
            plt.plot(xs, ratios, color=colors[schema_name], label=schema_name, linewidth=7.0)
            plt.xticks(fontsize=40)
            plt.yticks(fontsize=40)

plt.grid(True)
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), ncol=n_graphics, fontsize=25)
plt.savefig(f'stats/evolution/{"_".join(wanted_schemas)}.png')
