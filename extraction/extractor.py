from __future__ import annotations

import sys
from enum import Enum
from math import inf

from pysat.formula import CNF

from extraction.orchestra import fast_orchestra
from extraction.config import Config, CONFIG_STANDARD, CONFIG_PART, CONFIG_FULL, CONFIG_CLIPPED, CONFIG_SMALL
from extraction.fullscan import fullscan_border
from util.util import just_timeit


class FormulaSize(Enum):
    TINY = 10  # 1-10 variables
    SMALL = 100  # 11-100 variables
    MEDIUM = 1000  # 101-1000 variables
    BIG = 10000  # 1001-10000 variables
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
            ExtractionMode.STANDARD: self._orchestra_standard,
            ExtractionMode.ACCELERATED: self._orchestra_clipped,
            ExtractionMode.FAST: self._orchestra_small_size,
        }

    def _full_scan(self):
        self.inputs = fullscan_border.find_inputs(self.formula)

    def _orchestra_full(self):
        self._orchestra_with_config(CONFIG_FULL)

    def _orchestra_part(self):
        self._orchestra_with_config(CONFIG_PART)

    def _orchestra_standard(self):
        self._orchestra_with_config(CONFIG_STANDARD)

    def _orchestra_clipped(self):
        self._orchestra_with_config(CONFIG_CLIPPED)

    def _orchestra_small_size(self):
        self._orchestra_with_config(CONFIG_SMALL)

    def _orchestra_with_config(self, cfg: Config):
        self.inputs = fast_orchestra.find_inputs(self.formula, cfg)

    @just_timeit
    def extract(self, mode: ExtractionMode | None = None) -> list[int]:
        if mode is None:
            mode = self.mode

        solve_method = self._mode_to_algorithm[mode]
        solve_method()
        self.inputs.sort()

        return self.inputs


if __name__ == '__main__':
    ie = InputsExtractor(CNF(from_file=sys.argv[1]))
    ie.extract()
    print(len(ie.inputs))
    print(*ie.inputs)
