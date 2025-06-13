import os
from multiprocessing import freeze_support

from pysat.formula import CNF

from decomposition.estimation import DecompositionEstimation
from extraction.extractor import InputsExtractor
from util.util import inputs_outputs, remove_miter, extract_filenames, basename_noext, remove_zeroes


def extract_inputs(lec_instance: CNF):
    return InputsExtractor(lec_instance).extract()


def estimate_lecs(formulas: list[(CNF, str)], inputs: list[list[int]] | None = None):
    for (lec_instance, name), inp in zip(formulas, inputs or [None] * len(formulas)):
        if '01' in name:
            continue
        try:
            print(name)
            print('smth', file=stat_file, flush=True)
            if inp is None:
                lec_without_miter, miter = remove_miter(lec_instance)
                inp = extract_inputs(lec_without_miter)

                print(os.path.join('answers', 'extractor', f'{basename_noext(name)}.ans'))
                ans_file = open(os.path.join('answers', 'extractor', f'{basename_noext(name)}.ans'), 'w')
                print(len(inp), file=ans_file)
                print(*inp, file=ans_file)

            d = DecompositionEstimation(lec_instance, inp, assumption_time_limit=20)
            d.print_stats(use_lambdas=True, file=stat_file)
        except Exception as e:
            print(e)
            continue


if __name__ == '__main__':
    freeze_support()

    stat_file = open(os.path.join('stats', 'decomposition_stat_no_lambdas.stat'), 'w+')
    filenames_cnf = extract_filenames([os.path.join('tests', 'lec')], '.cnf')
    units = [fn for fn in filenames_cnf if 'unit' in fn]
    filenames_answers = extract_filenames([os.path.join('answers', 'extractor')], '.ans')

    filenames_answers = [fn for fn in filenames_answers if os.stat(fn).st_size > 0]

    filenames_cnf_noext = [basename_noext(fn) for fn in filenames_cnf]
    filenames_answers_noext = set([basename_noext(fn) for fn in filenames_answers])

    filenames_cnf_noext = [fn for fn in filenames_cnf_noext
                           if fn in filenames_answers_noext or
                           fn.split('_')[0] in filenames_answers_noext]

    filenames_cnf = [os.path.join('tests', 'lec', f'{fn}.cnf') for fn in filenames_cnf_noext]

    filenames_cnf.sort()
    filenames_answers.sort()
    units.sort(key=lambda x: CNF(from_file=x).nv)
    print(units)
    # print(filenames_cnf)

    estimate_lecs([(remove_zeroes(CNF(from_file=fn)), fn) for fn in units],
                  None)

