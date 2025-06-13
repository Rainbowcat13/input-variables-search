import os

from pysat.formula import CNF

from decomposition.estimation import DecompositionEstimation
from graphics.one_schema_dispersion_graphic import disp_graphic
from util.util import inputs_outputs
from util.util import basename_noext, extract_filenames, remove_zeroes

if __name__ == '__main__':
    # ex_files = list(filter(lambda file: basename_noext(file).startswith('ex'),
    #                        extract_filenames(['answers/extractor'], '.ans')))
    files = list(filter(lambda fn: 'unit' in fn, extract_filenames(['tests/inputs'], '.inputs')))
    stat_file = open('stats/units_tm.stat', 'w')

    for example in files:
        example = basename_noext(example)
        print(example, file=stat_file)
        print(example)
        inp_file = os.path.join('tests', 'inputs', f'{example}.inputs')
        cnf_file = os.path.join('tests', 'lec', f'{example}.cnf')
        ans_file = os.path.join('answers', 'extractor', f'{example}.ans')

        formula = remove_zeroes(CNF(from_file=cnf_file))

        try:
            inputs = inputs_outputs(inp_file)
            answer = inputs_outputs(ans_file)
        except Exception as e:
            print(e)
            continue

        d = DecompositionEstimation(formula, inputs, assumption_time_limit=10, estimation_vector_count=150)
        d.print_stats(file=stat_file)

        d2 = DecompositionEstimation(formula, answer, assumption_time_limit=10, estimation_vector_count=150)
        d2.compare_with_random(use_lambdas=True)

        random_times = d.times_random if len(inputs) < len(answer) else d2.times_random

        disp_graphic(d2.times_inputs, random_times,
                     save_to=f'graphics/disp_pics_units/{example}.png', data_ideal=d.times_inputs)
