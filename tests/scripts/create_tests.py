from __future__ import annotations

import os
import sys
import multiprocessing
import shutil

from pysat.formula import CNF
from pysat.solvers import Glucose3
import aigerox

from util.util import extract_filenames, mkdirs, CNFSchema, create_schemas_lec, map_var, shuffle_cnf, map_vars

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


def convert_aig(output_dir, aig, create_lec: bool = False, fix_inputs: bool = False) -> CNFSchema | None:
    schema_name = aig.split("/")[-1].split(".")[0]
    cnf_filename = f'{schema_name}.cnf'
    aag_filename = f'{schema_name}.aag'
    inputs_filename = f'{schema_name}.inputs'
    outputs_filename = f'{schema_name}.outputs'

    print(f'\nConverting {aig}...')
    if not aig.startswith(f'{output_dir}/aig/'):
        shutil.copy(aig, f'{output_dir}/aig/')
    os.system(f'aiger/aigtoaig {aig} {output_dir}/aag/{aag_filename}')
    try:
        parsed_aig = aigerox.Aig.from_file(f'{output_dir}/aag/{aag_filename}')
    except RuntimeError as err:
        print(f'Cannot parse aag {aag_filename}. Reason {err}')
        return

    clauses, mapping = parsed_aig.to_cnf()
    inputs = map_vars(mapping, parsed_aig.inputs())
    outputs = map_vars(mapping, parsed_aig.outputs())

    f = CNF(from_clauses=clauses)
    fixed_mapping = dict()
    if fix_inputs:
        fixed_mapping = {
            var: idx + 1
            for idx, var
            in enumerate(inputs)
        }

    shuffled, shuffled_mapping = shuffle_cnf(f, fixed_mapping)
    inputs = list(sorted(map_vars(shuffled_mapping, inputs)))
    outputs = list(sorted(map_vars(shuffled_mapping, outputs)))

    stat_file.write(f'{shuffled.nv}:{len(inputs)}\n')
    shuffled.to_file(f'{output_dir}/cnf/{cnf_filename}')
    for content, path in zip(
            [inputs, outputs],
            [f'{output_dir}/inputs/{inputs_filename}',
             f'{output_dir}/outputs/{outputs_filename}']
    ):
        with open(path, 'w') as content_file:
            content_file.write(f'{len(content)}\n{" ".join(map(str, content))}\n')

    schema = CNFSchema(shuffled, inputs, outputs)
    if create_lec:
        lec_schema = create_schemas_lec(schema, schema)
        lec_schema.to_file(f'{output_dir}/lec/{schema_name}_{schema_name}.cnf')

    return schema


def convert_verilog(output_dir, verilog):
    schema_name = verilog.split("/")[-1].split(".")[0]
    aig_path = f'{output_dir}/aig/{schema_name}.aig'
    with open('verilog_to_aig_template.ys', 'r') as template:
        yosys_script = template.read().replace('${V_INPUT_FILE}',
                                               verilog
                                               ).replace('${AIG_OUTPUT_FILE}',
                                                         aig_path)
    os.system(f'yosys -p "{yosys_script}"')
    return convert_aig(output_dir, aig_path, fix_inputs=True)


def create_lec_from_verilog(output_dir, v_dir):
    lec_instance_name = v_dir.split('/')[-1]
    schemas = []
    for v_file in os.listdir(v_dir):
        schemas.append(convert_verilog(output_dir, os.path.join(v_dir, v_file)))
    if len(schemas) != 2:
        print('Cannot create LEC instance on one or more than 2 schemas')
        return

    lec_schema = create_schemas_lec(*schemas)
    lec_schema.to_file(f'{output_dir}/lec/{lec_instance_name}.cnf')


if __name__ == '__main__':
    tests_dir = 'tests'

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
    mkdirs(f'{tests_dir}/aag', f'{tests_dir}/aig', f'{tests_dir}/cnf',
           f'{tests_dir}/inputs', f'{tests_dir}/outputs', f'{tests_dir}/lec')
    for file in files:
        convert_function(tests_dir, file, create_lec=True)
    print(f'SAT formulae: {tc.value}/{len(files)}')
    print(f'UNSAT formulae: {fc.value}/{len(files)}')
    print(f'Stuck or incorrect formulae: {len(files) - tc.value - fc.value}/{len(files)}')

    lec_instances_dir = 'hdl-benchmarks/iccad-2015'
    for d in os.listdir(lec_instances_dir):
        create_lec_from_verilog(tests_dir, os.path.join(lec_instances_dir, d))

    if os.path.exists(f'{tests_dir}/abc.history'):
        os.system(f'rm {tests_dir}/abc.history')
