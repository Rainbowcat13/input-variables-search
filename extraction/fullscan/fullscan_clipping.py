from pysat.formula import CNF
from pysat.solvers import Glucose3

from util.util import assumption_key, precount_set_order, var_frequency

formula = CNF(from_file='tests/cnf/example_formula.cnf')
number_vars = formula.nv
controversions_or_scanned = set()
non_output = set()
g = Glucose3(formula.clauses)
prop_cnt = 0
# Идея в том, чтобы перебирать переменные так, что если был найден набор с противоречиями,
# не перебирать никакие наборы, содержащие этот


def scan(not_used: dict[int, int], assumption: list[int]):
    # используем dict в not_used для сохранения порядка перебора
    global prop_cnt
    fs_key = frozenset(assumption)

    if fs_key in controversions_or_scanned:
        return

    abs_key = frozenset(assumption_key(assumption))
    if abs_key not in non_output:
        prop_cnt += 1
        no_conflicts, result = g.propagate(assumption)
        if not no_conflicts:
            controversions_or_scanned.add(fs_key)
            non_output.add(abs_key)
            return
        if len(result) < number_vars:
            non_output.add(abs_key)
        # Если какая-то переменная вывелась из текущей подстановки, нам не нужно перебирать ее значение далее
        # Почему-то это делает только хуже на методе с предподсчетом
        for var_num in result:
            if var_num in not_used:
                not_used.pop(var_num)

    for var_num, var_freq in not_used.items():
        for sign in [1, -1]:
            assumption.append(sign * var_num)
            new_not_used = not_used.copy()
            new_not_used.pop(var_num)
            scan(new_not_used, assumption)
            not_used[var_num] = var_freq
            new_not_used.clear()
            assumption.pop()

    controversions_or_scanned.add(fs_key)


def find_minimal(start_level=0):
    minimal_set = [i + 1 for i in range(number_vars)]
    for i in range(2 ** number_vars):
        if bin(i).count('1') < start_level:
            continue
        assumptions = [j + 1 for j in range(number_vars) if (2 ** j) & i]
        if frozenset(assumptions) not in non_output and len(assumptions) < len(minimal_set):
            minimal_set = assumptions + []

    return minimal_set


not_used_start = var_frequency(formula)
# Возможно, если брать переменные не в случайном порядке, а пытаться перебрать сначала те, которые встречаются чаще,
# удовлетворительное решение найдется быстрее
scan(not_used_start, [])
answer = find_minimal()

print(len(answer))
print(*answer)
print(f'Complexity: {prop_cnt}')

# Что если посчитать для всех комбинаций переменных небольшой мощности,
# сколько суммарно из них выводится при разных подстановках?
# Получится порядок на маленьких комбинациях, и как будто, приоритетнее рассматривать те,
# которые выводят больше переменных

scan_order = precount_set_order(formula, g, level=2)
controversions_or_scanned.clear()
non_output.clear()
prop_cnt = 0

not_used = var_frequency(formula)
for assumption in scan_order:
    scan({key: value for key, value in not_used.items() if key not in assumption}, assumption)
    # Здесь, после того как нашли какое-то решение, удовлетворяющее по размеру, можно отрубить дальнейший поиск
    # Можно ли это распараллелить? Кажется, да, есть две мапы и целое число, зашаренные между вызовами
    # Не в питоне, разумеется

answer = find_minimal(start_level=2)
print(len(answer))
print(*answer)
print(f'Complexity: {prop_cnt}')
