from __future__ import annotations

from enum import Enum
from math import inf

from pysat.formula import CNF

from extraction.fullscan import fullscan_border
from util.util import timeit


class FormulaSize(Enum):
    TINY = 10      # 1-10 variables
    SMALL = 100    # 11-100 variables
    MEDIUM = 1000  # 101-1000 variables
    BIG = 10000    # 1001-10000 variables
    HUGE = 100000  # 10001-100000 variables
    MASSIVE = inf  # 100001+ variables

    @classmethod
    def from_formula(cls, formula):
        return next(size for size in cls if formula.nv <= size.value)


class ExtractionMode(Enum):
    FULL = 'full'
    SLOW = 'slow'
    EXTENDED = 'extended'
    STANDARD = 'standard'
    ACCELERATED = 'accelerated'
    FAST = 'fast'


SIZE_TO_MODE = {
    FormulaSize.TINY: ExtractionMode.FULL,
    FormulaSize.SMALL: ExtractionMode.SLOW,
    FormulaSize.MEDIUM: ExtractionMode.EXTENDED,
    FormulaSize.BIG: ExtractionMode.STANDARD,
    FormulaSize.HUGE: ExtractionMode.ACCELERATED,
    FormulaSize.MASSIVE: ExtractionMode.FAST
}


class InputsExtractor:
    def __init__(self, formula: CNF):
        self.formula = formula
        self.size = FormulaSize.from_formula(formula)
        self.mode = SIZE_TO_MODE[self.size]
        self.inputs = None
        self._mode_to_algorithm = {
            ExtractionMode.FULL: self._full_scan,
            ExtractionMode.SLOW: self._orchestra_full,
            ExtractionMode.EXTENDED: self._orchestra_part,
            ExtractionMode.STANDARD: self._orchestra_part,
            ExtractionMode.ACCELERATED: self._orchestra_clipped,
            ExtractionMode.FAST: self._orchestra_small_size,
        }

    def _full_scan(self):
        self.inputs = fullscan_border.find_inputs(self.formula)

    def _orchestra_full(self):
        pass

    def _orchestra_part(self):
        pass

    def _orchestra_clipped(self):
        pass

    def _orchestra_small_size(self):
        pass

    @timeit
    def extract(self, mode: ExtractionMode | None = None) -> list[int]:
        if mode is None:
            mode = self.mode

        solve_method = self._mode_to_algorithm[mode]
        solve_method()

        return self.inputs


if __name__ == '__main__':
    ie = InputsExtractor(CNF(from_file='tests/cnf/example_formula.cnf'))
    ie.extract()
    print(len(ie.inputs))
    print(*ie.inputs)
