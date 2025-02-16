from pysat.formula import CNF
from pysat.solvers import Glucose3


formula = CNF(from_file='formula.cnf')
number_vars = formula.nv


def scan():
    pass
    # Идея в том, чтобы перебирать переменные так, что если был найден набор с противоречиями,
    # не перебирать никакие наборы, содержащие этот
