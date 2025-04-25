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
    small_expansion_no_sample: bool = False
    input_size_upper_bound: int = 1500
    expansion_candidates_count: int = 1
    score_method: ScoreMethod = ScoreMethod.TOTAL
    use_pool: bool = True
    evolution_generations_count: int = 10000
    expansion_start_size: int = 5
    expansion_sample_size: int = 700
    cut_iterations_count: int = 5
    cut_conflict_border: float = 0.0


CONFIG_FULL = Config(
    random_seed=13,
    break_on_decline=False,
    zero_conflict_tolerance=False,
    expansion_conflict_border=0.9,
    estimation_vector_count=1000,
    big_expansion_no_sample=True,
    small_expansion_no_sample=True,
    input_size_upper_bound=128,
    expansion_candidates_count=3,
    score_method=ScoreMethod.TOTAL,
    use_pool=True,
    evolution_generations_count=10000,
    expansion_start_size=6,
    expansion_sample_size=700,
    cut_iterations_count=64,
    cut_conflict_border=0.0
)

CONFIG_PART = Config(
    random_seed=13,
    break_on_decline=False,
    zero_conflict_tolerance=False,
    expansion_conflict_border=0.9,
    estimation_vector_count=1000,
    big_expansion_no_sample=True,
    small_expansion_no_sample=False,
    input_size_upper_bound=256,
    expansion_candidates_count=1,
    score_method=ScoreMethod.TOTAL,
    use_pool=True,
    evolution_generations_count=10000,
    expansion_start_size=5,
    expansion_sample_size=700,
    cut_iterations_count=32,
    cut_conflict_border=0.0
)

CONFIG_STANDARD = Config(
    random_seed=13,
    break_on_decline=False,
    zero_conflict_tolerance=False,
    expansion_conflict_border=0.9,
    estimation_vector_count=500,
    big_expansion_no_sample=False,
    small_expansion_no_sample=False,
    input_size_upper_bound=1024,
    expansion_candidates_count=1,
    score_method=ScoreMethod.TOTAL,
    use_pool=True,
    evolution_generations_count=10000,
    expansion_start_size=4,
    expansion_sample_size=1000,
    cut_iterations_count=16,
    cut_conflict_border=0.0
)

CONFIG_CLIPPED = Config(
    random_seed=13,
    break_on_decline=True,
    zero_conflict_tolerance=False,
    expansion_conflict_border=0.3,
    estimation_vector_count=100,
    big_expansion_no_sample=False,
    small_expansion_no_sample=False,
    input_size_upper_bound=2048,
    expansion_candidates_count=1,
    score_method=ScoreMethod.TOTAL,
    use_pool=True,
    evolution_generations_count=1000,
    expansion_start_size=3,
    expansion_sample_size=7000,
    cut_iterations_count=5,
    cut_conflict_border=0.0
)

CONFIG_SMALL = Config(
    random_seed=13,
    break_on_decline=True,
    zero_conflict_tolerance=True,
    expansion_conflict_border=0.1,
    estimation_vector_count=100,
    big_expansion_no_sample=False,
    small_expansion_no_sample=False,
    input_size_upper_bound=2048,
    expansion_candidates_count=1,
    score_method=ScoreMethod.TOTAL,
    use_pool=True,
    evolution_generations_count=250,
    expansion_start_size=2,
    expansion_sample_size=7500,
    cut_iterations_count=5,
    cut_conflict_border=0.0
)
