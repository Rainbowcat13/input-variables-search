import os
import sys
from pathlib import Path

import aiger
from aiger_cnf import aig2cnf
from pysat.formula import CNF

sys.setrecursionlimit(10 ** 9)

output_dir = 'tests'
if len(sys.argv) > 1:
    output_dir = sys.argv[1]

aig_dirs = ['benchmarks/arithmetic', 'benchmarks/random_control']
aig_files = [
    str(file.absolute())
    for file in sum([
        list(Path(d).glob('**/*'))
        for d in aig_dirs
    ], [])
    if file.name.endswith('.aig')
]

for aig in aig_files:
    cnf_filename = f'{aig.split("/")[-1].split(".")[0]}.cnf'
    inputs_filename = cnf_filename.replace('.cnf', '.inputs')
    if os.path.exists(f'{output_dir}/{cnf_filename}'):
        print(f'File {cnf_filename} already exists. To regenerate clear {output_dir}.')
    else:
        print(f'\nConverting {aig}...')
        schema = aiger.load(aig)
        cnf = aig2cnf(schema)
        inputs = list(sorted(cnf.input2lit.values()))
        CNF(from_clauses=cnf.clauses).to_file(f'{output_dir}/{cnf_filename}')
        with open(f'{output_dir}/{inputs_filename}', 'w') as inputs_file:
            inputs_file.write(f'{len(inputs)}\n{" ".join(map(str, inputs))}\n')

if os.path.exists('abc.history'):
    os.system('rm abc.history')
