import os

from pysat.formula import CNF

from graphics.lec_dispersions_graphics import cov_graphic
from graphics.one_schema_dispersion_graphic import disp_graphic
from util.util import var_coeff

file = open('stats/sat_disp_stats.stat', 'r')


def read_floats(s):
    return [float(x) for x in s.split()]


lines = file.readlines()
rand_tms = []
inp_tms = []
formulae = []
names = []
for i, line in enumerate(lines):
    line = line.strip()

    if line.startswith('Formula:'):
        tr = read_floats(lines[i + 10])
        ti = read_floats(lines[i + 12])

        if all(t >= 5 for t in tr) or all(t >= 5 for t in ti):
            continue

        print(lines[i + 4].split()[-1])
        names.append(line.split()[-1])
        formulae.append(CNF(from_file=os.path.join('tests', 'sat2021', f'{line.split()[-1]}.cnf')))
        rand_tms.append(tr)
        inp_tms.append(ti)

vcr = []
vci = []
xs = []
for nm, f, r, i in sorted(zip(names, formulae, rand_tms, inp_tms), key=lambda p: p[1].nv):
    # disp_graphic(i, r, save_to=f'graphics/dispsat_{nm}.png')
    vcr.append(var_coeff(r))
    vci.append(var_coeff(i))
    xs.append(f'{f.nv}')

cov_graphic(vci, vcr, save_to='stats/sat2021_var_coeff.png', xs=xs)
