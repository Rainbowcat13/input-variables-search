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

plt.figure(figsize=(12, 8), dpi=150)
plt.xlabel('Количество переменных в стартовом множестве')
plt.ylabel('Доля конфликтующих подстановок')
plt.title('Скорость роста доли конфликтов от размера множества для некоторых схем')

for file in os.listdir('stats/evolution'):
    with open(os.path.join('stats/evolution', file), 'r') as stat_file:
        schema_name = file.replace('.stat', '')
        if schema_name in wanted_schemas:
            ratios = [float(line.strip().split()[1]) for line in stat_file.readlines()]
            xs = list(range(1, len(ratios) + 1))
            plt.plot(xs, ratios, color=colors[schema_name], label=schema_name)

plt.grid(True)
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.07), ncol=len(wanted_schemas))
plt.savefig(f'stats/evolution/{"_".join(wanted_schemas)}.png')
