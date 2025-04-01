import os
import sys
import multiprocessing
import shutil

from pysat.formula import CNF
from pysat.solvers import Glucose3
import aigerox

from util import extract_filenames, mkdirs


sys.setrecursionlimit(10 ** 9)
tc = multiprocessing.Value('i', 0)
fc = multiprocessing.Value('i', 0)


def try_solve(f, cnt1, cnt2):
    result = Glucose3(bootstrap_with=f.clauses).solve()
    print(f'Solved with result: {result}')
    with cnt1.get_lock():
        cnt1.value += int(result)
    with cnt2.get_lock():
        cnt2.value += (1 - int(result))


def check_sat(f):
    print('Try solve...')
    p = multiprocessing.Process(target=try_solve, args=(f, tc, fc))
    p.start()
    p.join(15)
    if p.is_alive():
        print('Solving stuck, exiting')
        p.kill()
        p.join()


def convert_blif(output_dir, blf):
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
        f = CNF(from_file=f'{output_dir}/{cnf_filename}')
        check_sat(f)


def convert_aig(output_dir, aig):
    cnf_filename = f'{aig.split("/")[-1].split(".")[0]}.cnf'
    aag_filename = cnf_filename.replace('.cnf', '.aag')
    inputs_filename = cnf_filename.replace('.cnf', '.inputs')

    mkdirs(f'{output_dir}/aag', f'{output_dir}/aig', f'{output_dir}/cnf', f'{output_dir}/inputs')

    print(f'\nConverting {aig}...')
    shutil.copy(aig, f'{output_dir}/aig/')
    os.system(f'aiger/aigtoaig {aig} {output_dir}/aag/{aag_filename}')
    parsed_aig = aigerox.Aig.from_file(f'{output_dir}/aag/{aag_filename}')

    inputs = parsed_aig.inputs()
    clauses, mapping = parsed_aig.to_cnf()
    inputs = list(sorted([mapping[x] for x in inputs]))
    f = CNF(from_clauses=clauses)
    f.to_file(f'{output_dir}/cnf/{cnf_filename}')
    with open(f'{output_dir}/inputs/{inputs_filename}', 'w') as inputs_file:
        inputs_file.write(f'{len(inputs)}\n{" ".join(map(str, inputs))}\n')
    check_sat(f)


if __name__ == '__main__':
    output_dir = 'tests'

    benchmarks_dirs = ['benchmarks/arithmetic',
                       'benchmarks/random_control',]
                       # 'iwls2024-ls-contest/submissions/USTC_and_Huawei/aig']
    aig_files = extract_filenames(benchmarks_dirs, '.aig')
    blif_files = extract_filenames(benchmarks_dirs, '.blif')

    files = blif_files
    convert_function = convert_blif
    if '--aig' in sys.argv:
        convert_function = convert_aig
        files = aig_files
    for file in files:
        convert_function(output_dir, file)
    print(f'SAT formulae: {tc.value}/{len(files)}')
    print(f'UNSAT formulae: {fc.value}/{len(files)}')
    print(f'Stuck formulae: {len(files) - tc.value - fc.value}/{len(files)}')

    if os.path.exists(f'{output_dir}/abc.history'):
        os.system(f'rm {output_dir}/abc.history')
