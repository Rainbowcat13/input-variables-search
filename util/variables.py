from pysat.formula import CNF


def unit_propagation(formula: CNF) -> (bool, CNF):
    new_formula = CNF(from_clauses=formula.clauses)
    for variable in range(1, formula.nv + 1):
        alone_pos = False
        alone_neg = False
        pos = set()
        neg = set()
        neutral = set()
        clauses = formula.clauses.copy()
        for index, clause in enumerate(clauses):
            if clause == [variable]:
                pos.add(index)
                alone_pos = True
            elif clause == -variable:
                neg.add(index)
                alone_neg = True
            elif variable in clause:
                pos.add(index)
            elif -variable in clause:
                neg.add(index)
            else:
                neutral.add(index)

        result_clauses = clauses.copy()
        if alone_neg and alone_pos:
            raise ValueError('Unsatisfiable formula')
        elif alone_pos:
            result_clauses = [
                [var for var in clause if var != -variable]
                if index in neg
                else clause
                for index, clause in enumerate(clauses)
                if index not in pos
            ]
        elif alone_neg:
            result_clauses = [
                [var for var in clause if var != variable]
                if index in pos
                else clause
                for index, clause in enumerate(clauses)
                if index not in neg
            ]

        new_formula = CNF(from_clauses=result_clauses)

    if new_formula.clauses != formula.clauses:
        return True, new_formula
    else:
        return False, new_formula


def simplify(formula: CNF) -> CNF:
    changed, new_formula = unit_propagation(formula)
    while changed:
        changed, new_formula = unit_propagation(new_formula)
    return new_formula


if __name__ == '__main__':
    f = CNF(from_file='../tests/cnf/example_formula.cnf')
    new_f = simplify(f)
    print(new_f.clauses)
    print(f.clauses == new_f.clauses)
