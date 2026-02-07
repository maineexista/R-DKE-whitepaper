"""
Experiments Package for R-DKE Validation
"""

from .experiment_1_contradiction_pressure import run_experiment as run_contradiction_test
from .experiment_2_gap_fill import run_experiment as run_gap_fill_test
from .experiment_3_forgetfulness import run_experiment as run_forgetfulness_test

__all__ = [
    "run_contradiction_test",
    "run_gap_fill_test", 
    "run_forgetfulness_test"
]
