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
plt.ylabel('Количество схем с таким значением', fontsize=40)
plt.xlabel('Диапазоны значений доли выведенных', fontsize=40)
plt.title('Оценка корректности алгоритма нахождения входов.\nСредняя доля выведенных переменных на подстановку', fontsize=40)

totals = np.array([])
jaccards = np.array([])
for file in sorted(filter(lambda f: f.endswith('.check') and 'ex' in f, os.listdir('answers/extractor')),
                   key=lambda x: int(x.split('.')[0].strip('ex'))):
    print(file)
    # if 'ex60' in file:
    #     print('pizda')
    #     break
    metrics = Metrics(filename=os.path.join('answers/extractor', file))
    totals = np.append(totals, metrics.propagation)
    print(metrics.jaccard)
    jaccards = np.append(jaccards, metrics.jaccard)

n = len(totals)
idxs = list(range(1, n + 1))

thresholds = np.arange(0.05, 1.01, 0.05)
counts = [
    sum([
        (thresholds[i - 1] if i > 0 else 0) <= j <= thresholds[i]
        for j in totals
    ]) for i in range(len(thresholds))
]

print(counts)
print([f'{t:.2f}' for t in thresholds])
plt.bar([f'{t:.2f}' for t in thresholds], counts, color='blue')
plt.xticks(fontsize=20)
plt.yticks(fontsize=40)
plt.grid(True)
plt.savefig('stats/prop.png')
# plt.show()
