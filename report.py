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
        if len(lines := ans_f.readlines()) == 2:
            correct_inputs = [int(x) for x in lines[1].strip().split()]
        else:
            print(f'.ans file corrupted, no report for {ans_file}')
            return

    formula = CNF(from_file=cnf_file)
    prop_ratio, conflicts_ratio = fitness(Glucose3(formula), program_inputs, 100000)

    lv_res = f'Levenshtein distance from real input: {Levenshtein.distance(program_inputs, correct_inputs)}'
    match_res = (f'Match with real input: '
                 f'{round(len(set(program_inputs) & set(correct_inputs)) / len(correct_inputs), 7) * 100}%')
    prop_res = f'Propagation: {round(prop_ratio / formula.nv, 7) * 100}%'
    cfl_res = f'Conflicts: {round(conflicts_ratio, 7) * 100}%'
    total_result.extend([f'Results for {basename_noext(cnf_file)}, solution method {solution_name(ans_file)}:',
                         '\t' + lv_res, '\t' + match_res, '\t' + prop_res, '\t' + cfl_res, ''])

    with open(report_file, 'w') as rpf:
        for res_piece in [lv_res, match_res, prop_res, cfl_res]:
            print(res_piece, file=rpf)


cnf_files = list(sorted(extract_filenames(['tests/cnf'], '.cnf')))
input_files = list(sorted(extract_filenames(['tests/inputs'], '.inputs')))
ans_files = list(sorted(extract_filenames(['answers/fast_orchestra/fasten'], '.ans')))
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

print(f'Checked {ans_count} answers from {cnf_count} formulas. Full report is available in {full_report_filename}')
