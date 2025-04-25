import os
from dataclasses import dataclass, fields

import matplotlib.pyplot as plt
import numpy as np

from util.util import extract_filenames


@dataclass
class Metrics:
    levenshtein: int
    match: float
    propagation: float
    conflicts: float
    total: float
    jaccard: float

    def from_file(self, filename):
        with open(filename, 'r') as check_file:
            lines = [line.strip() for line in check_file.readlines()]

        for line in lines:
            value_type, value = line.split(': ')
            if value.endswith('%'):
                parsed_value = float(value.strip('%')) / 100
            else:
                parsed_value = float(value)

            value_type = value_type.lower()
            for field in fields(self):
                if field.name in value_type:
                    setattr(self, field.name, parsed_value)
                    break

    def __init__(self, filename: str):
        self.from_file(filename)


plt.figure(figsize=(24, 16), dpi=300)
plt.ylabel('Количество схем с такой метрикой', fontsize=40)
plt.xlabel('Диапазон метрик', fontsize=40)
plt.title('Оценка корректности алгоритма нахождения входов', fontsize=40)

totals = np.array([])
jaccards = np.array([])
for file in extract_filenames(['answers/fast_orchestra/extra_slow'], '.check'):
    metrics = Metrics(filename=os.path.join('answers/fast_orchestra/extra_slow', file))
    totals = np.append(totals, metrics.total)
    jaccards = np.append(jaccards, metrics.jaccard)

n = len(totals)
idxs = list(range(1, n + 1))

thresholds = np.arange(0.05, 1, 0.05)
counts = [
    sum([
        (thresholds[i - 1] if i > 0 else 0) <= j < thresholds[i]
        for j in jaccards
    ]) for i in range(len(thresholds))
]

plt.bar([f'{t:.2f}' for t in thresholds], counts, color='green')
plt.xticks(fontsize=20)
plt.yticks(fontsize=40)
plt.grid(True)
plt.savefig('stats/jaccards.png')
