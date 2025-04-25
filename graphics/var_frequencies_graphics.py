import os
import sys

from more_itertools import chunked

from pysat.formula import CNF
import matplotlib.pyplot as plt
from tqdm import tqdm

from util.util import var_frequency, extract_filenames, basename_noext, inputs_outputs


CHUNKS_COUNT = 10


total_distribution = []
for cnf_filename in tqdm(os.listdir('tests/cnf'), file=sys.stderr, desc='Distributing'):
    cnf_filename = os.path.join('tests/cnf', cnf_filename)
    bn = basename_noext(cnf_filename)

    formula = CNF(from_file=cnf_filename)
    inputs = set(inputs_outputs(os.path.join('tests/inputs', f'{bn}.inputs')))

    freq = var_frequency(formula)
    chunks = list(chunked(freq, CHUNKS_COUNT))

    total_distribution = [was + len(set(chunk) & inputs) for was, chunk in zip(total_distribution, chunks)]


plt.figure(figsize=(24, 16), dpi=300)
plt.ylabel('Количество входов', fontsize=40)
plt.xlabel('Топ K% по встречаемости', fontsize=40)
plt.title('Частота встречаемости входов\nкак переменных в формуле', fontsize=40)
plt.bar([f'{p}%' for p in range(10, 101, 10)], total_distribution, color='red')
plt.xticks(fontsize=20)
plt.yticks(fontsize=40)
plt.grid(True)
plt.savefig('stats/inputs_distribution.png')
plt.show()
