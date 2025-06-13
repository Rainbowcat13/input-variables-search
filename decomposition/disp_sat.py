import os

from pysat.formula import CNF

from decomposition.estimation import DecompositionEstimation
from util.util import inputs_outputs, basename_noext, score, ScoreMethod, percents

ESTIMATION_VECTOR_COUNT = 1000


if __name__ == '__main__':
    sat2021_answers_dir = os.path.join('answers', 'sat2021')
    sat2021_answers = os.listdir(sat2021_answers_dir)

    for ans_file in sat2021_answers:
        formula_name = basename_noext(ans_file)
        fname_wout_id = formula_name.split('-')[1]

        f = CNF(from_file=os.path.join('tests', 'sat2021', f'{formula_name}.cnf'))
        possible_inputs = inputs_outputs(os.path.join(sat2021_answers_dir, ans_file))
        d = DecompositionEstimation(formula=f, inputs=possible_inputs, assumption_time_limit=5)

        pts_prop = score(f, d.solver, possible_inputs, ESTIMATION_VECTOR_COUNT, ScoreMethod.PROP)
        pts_cfl = score(f, d.solver, possible_inputs, ESTIMATION_VECTOR_COUNT, ScoreMethod.CONFLICTS)

        print(f'Formula: {formula_name}')
        print(f'Input set size (% from formula size): {percents(len(possible_inputs) / f.nv)}%')
        print(f'Points propagation: {percents(pts_prop)}%')
        print(f'Conflicts ratio: {percents(-pts_cfl)}%')

        d.print_stats(use_lambdas=True)
