from dataclasses import dataclass

from util.util import ScoreMethod


@dataclass
class Config:
    random_seed: int = 13
    break_on_decline: bool = True
    zero_conflict_tolerance: bool = False
    expansion_conflict_border: float = 0.45
    estimation_vector_count: int = 250
    big_expansion_no_sample: bool = False
    input_size_upper_bound: int = 1500
    expansion_candidates_count: int = 1
    score_method: ScoreMethod = ScoreMethod.TOTAL
    use_pool: bool = True
    evolution_generations_count: int = 10000
    expansion_start_size: int = 5
    expansion_sample_size: int = 700
    cut_iterations_count: int = 5
    cut_conflict_border: float = 0.0
