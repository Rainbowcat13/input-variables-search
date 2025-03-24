import os
import sys
from pathlib import Path

import aiger
from aiger_cnf import aig2cnf
from pysat.formula import CNF

sys.setrecursionlimit(10 ** 9)


def extract_filenames(dirs, extension):
    return [
        str(file.absolute())
        for file in sum([
            list(Path(d).glob('**/*'))
            for d in benchmarks_dirs
        ], [])
        if file.name.endswith(extension)
    ]


def convert_blif(output_dir, blf):
    # Конвертирует вроде бы правильно, но нет функциональности вытащить входы
    # на самом деле тоже не очень-то правильно, adder получается unsat формулой
    cnf_filename = f'{blf.split("/")[-1].split(".")[0]}.cnf'
    if os.path.exists(f'{output_dir}/{cnf_filename}'):
        print(f'File {cnf_filename} already exists. To regenerate clear {output_dir}.')
    else:
        print(f'\nConverting {blf}...')
        os.system(
            f'abc/abc -c "read_blif {blf};'
            f' strash; '
            f'write_cnf {output_dir}/{cnf_filename}"'
        )


def convert_aig(output_dir, aig):
    # Неправильно конвертирует, делая из SAT формулы UNSAT
    cnf_filename = f'{aig.split("/")[-1].split(".")[0]}.cnf'
    inputs_filename = cnf_filename.replace('.cnf', '.inputs')
    if os.path.exists(f'{output_dir}/{cnf_filename}'):
        print(f'File {cnf_filename} already exists. To regenerate clear {output_dir}.')
    else:
        print(f'\nConverting {aig}...')
        schema = aiger.load(aig)
        cnf = aig2cnf(schema)
        inputs = list(sorted(cnf.input2lit.values()))
        # f = CNF(from_clauses=cnf.clauses)
        # g = Glucose3(bootstrap_with=f.clauses)
        # print('Try solve...')
        # if aig.endswith('adder.aig'):
        #     print(g.solve())
        CNF(from_clauses=cnf.clauses).to_file(f'{output_dir}/{cnf_filename}')
        with open(f'{output_dir}/{inputs_filename}', 'w') as inputs_file:
            inputs_file.write(f'{len(inputs)}\n{" ".join(map(str, inputs))}\n')


if __name__ == '__main__':
    output_dir = 'tests'
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]

    benchmarks_dirs = ['benchmarks/arithmetic', 'benchmarks/random_control']
    aig_files = extract_filenames(benchmarks_dirs, '.aig')
    blif_files = extract_filenames(benchmarks_dirs, '.blif')

    files = blif_files
    convert_function = convert_blif
    if '--aig' in sys.argv:
        convert_function = convert_aig
        files = aig_files
    for file in files:
        convert_function(output_dir, file)

    if os.path.exists(f'{output_dir}/abc.history'):
        os.system(f'rm {output_dir}/abc.history')
