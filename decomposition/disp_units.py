import os

from pysat.formula import CNF

from decomposition.lec import compare_inputs
from graphics.one_schema_dispersion_graphic import disp_graphic
from util.util import basename_noext, extract_filenames, remove_zeroes

if __name__ == '__main__':
    files = extract_filenames(['tests/lec'], '.cnf')
    stat_file = open('stats/schemas_all_tm.stat', 'w')

    for example in files:
        example = basename_noext(example)
        print(example, file=stat_file)
        print(example)
        sn = example.split('_')[0]
        inp_file = os.path.join('tests', 'inputs', f'{sn}.inputs')
        cnf_file = os.path.join('tests', 'lec', f'{example}.cnf')
        ans_file = os.path.join('answers', 'extractor', f'{sn}.ans')

        formula = remove_zeroes(CNF(from_file=cnf_file))

        cmp = compare_inputs(formula, inp_file, ans_file, res_file=stat_file)
        if cmp is None:
            continue
        tms_inputs, tms_answer, tms_random = cmp

        disp_graphic(tms_answer, tms_random,
                     save_to=f'graphics/disp_pics_all/{example}.png', data_ideal=tms_inputs)
