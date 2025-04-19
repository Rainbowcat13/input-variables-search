import os
import sys
import multiprocessing
import shutil

from pysat.formula import CNF
from pysat.solvers import Glucose3
import aigerox

from util import extract_filenames, mkdirs, CNFSchema, create_schemas_lec

sys.setrecursionlimit(10 ** 9)
tc = multiprocessing.Value('i', 0)
fc = multiprocessing.Value('i', 0)
stat_file = open('stats/inputs.stat', 'w')


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


# do not use
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


def map_var(mapping: dict[int, int], var: int) -> int:
    if var > 0:
        return mapping[var]
    elif var < 0:
        return -mapping[-var]
    return 0


def convert_aig(output_dir, aig):
    schema_name = aig.split("/")[-1].split(".")[0]
    cnf_filename = f'{schema_name}.cnf'
    aag_filename = f'{schema_name}.aag'
    inputs_filename = f'{schema_name}.inputs'
    outputs_filename = f'{schema_name}.outputs'

    print(f'\nConverting {aig}...')
    shutil.copy(aig, f'{output_dir}/aig/')
    os.system(f'aiger/aigtoaig {aig} {output_dir}/aag/{aag_filename}')
    try:
        parsed_aig = aigerox.Aig.from_file(f'{output_dir}/aag/{aag_filename}')
    except RuntimeError as err:
        print(f'Cannot parse aag {aag_filename}. Reason {err}')
        return

    inputs = parsed_aig.inputs()
    outputs = parsed_aig.outputs()
    clauses, mapping = parsed_aig.to_cnf()
    inputs = list(sorted([map_var(mapping, x) for x in inputs]))
    outputs = list(sorted([map_var(mapping, x) for x in outputs]))
    f = CNF(from_clauses=clauses)
    stat_file.write(f'{f.nv}:{len(inputs)}\n')
    f.to_file(f'{output_dir}/cnf/{cnf_filename}')
    for content, path in zip(
            [inputs, outputs],
            [f'{output_dir}/inputs/{inputs_filename}',
             f'{output_dir}/outputs/{outputs_filename}']
    ):
        with open(path, 'w') as content_file:
            content_file.write(f'{len(content)}\n{" ".join(map(str, content))}\n')
    schema = CNFSchema(f, inputs, outputs)
    lec_schema = create_schemas_lec(schema, schema)
    lec_schema.to_file(f'{output_dir}/lec/{schema_name}_{schema_name}.cnf')
    check_sat(f)


if __name__ == '__main__':
    output_dir = 'tests'

    benchmarks_dirs = ['benchmarks/arithmetic',
                       'benchmarks/random_control',
                       'iwls2024-ls-contest/submissions/USTC_and_Huawei/aig']
    aig_files = extract_filenames(benchmarks_dirs, '.aig')
    blif_files = extract_filenames(benchmarks_dirs, '.blif')

    files = blif_files
    convert_function = convert_blif
    if '--aig' in sys.argv:
        convert_function = convert_aig
        files = aig_files
    mkdirs(f'{output_dir}/aag', f'{output_dir}/aig', f'{output_dir}/cnf',
           f'{output_dir}/inputs', f'{output_dir}/outputs', f'{output_dir}/lec')
    for file in files:
        convert_function(output_dir, file)
    print(f'SAT formulae: {tc.value}/{len(files)}')
    print(f'UNSAT formulae: {fc.value}/{len(files)}')
    print(f'Stuck or incorrect formulae: {len(files) - tc.value - fc.value}/{len(files)}')

    if os.path.exists(f'{output_dir}/abc.history'):
        os.system(f'rm {output_dir}/abc.history')
