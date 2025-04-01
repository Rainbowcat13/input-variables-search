import os

import Levenshtein
from pysat.formula import CNF
from pysat.solvers import Glucose3

from util import fitness, extract_filenames, basename_noext, mkdirs

total_result = []


def solution_name(ans_filename):
    return os.path.dirname(ans_filename.split('answers/')[-1])


def write_check_result(cnf_file, inputs_file, ans_file, report_file):
    with open(inputs_file, "r") as inp_f:
        program_inputs = [int(x) for x in inp_f.readlines()[1].strip().split()]
    with open(ans_file, "r") as ans_f:
        correct_inputs = [int(x) for x in ans_f.readlines()[1].strip().split()]

    formula = CNF(from_file=cnf_file)
    prop_ratio, conflicts_ratio = fitness(Glucose3(formula), program_inputs, 100000)

    lv_res = f'Levenshtein: {Levenshtein.distance(program_inputs, correct_inputs)}'
    prop_res = f'Propagation: {round(prop_ratio / formula.nv, 7) * 100}%'
    cfl_res = f'Conflicts: {round(conflicts_ratio, 7) * 100}%'
    total_result.extend([f'Results for {basename_noext(cnf_file)}, solution method {solution_name(ans_file)}:',
                         '\t' + lv_res, '\t' + prop_res, '\t' + cfl_res, ''])

    with open(report_file, 'w') as rpf:
        print(lv_res, file=rpf)
        print(prop_res, file=rpf)
        print(cfl_res, file=rpf)


cnf_files = list(sorted(extract_filenames(['tests/cnf'], '.cnf')))
input_files = list(sorted(extract_filenames(['tests/inputs'], '.inputs')))
ans_files = list(sorted(extract_filenames(['answers/orchestra/prop'], '.ans')))
ans_count = len(ans_files)
cnf_count = len(cnf_files)

iter_ans = 0
iter_cnf = 0
print('Checking answers...')
while iter_ans < ans_count:
    while iter_cnf < cnf_count and \
            basename_noext(ans_files[iter_ans]) != basename_noext(cnf_files[iter_cnf]):
        iter_cnf += 1
    if iter_cnf == cnf_count:
        break

    report_filename = (f'{os.path.dirname(ans_files[iter_ans])}/'
                       f'{basename_noext(ans_files[iter_ans])}.check')
    write_check_result(cnf_files[iter_cnf], input_files[iter_cnf], ans_files[iter_ans], report_filename)
    iter_ans += 1

print('Generating report...')
mkdirs('reports')
reports = extract_filenames(['reports'], '.report')
max_report_num = max([0] + [int(rp.split('.')[-2].split('-')[-1]) for rp in reports])
full_report_filename = f'reports/rp-{max_report_num + 1}.report'
with open(full_report_filename, 'w') as rp_file:
    rp_file.write('\n'.join(total_result))

print(f'Checked {ans_count} answer from {cnf_count} formulas. Full report is available in {full_report_filename}')
