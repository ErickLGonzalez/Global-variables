"""B12-RGRC — Rival-grammar recovery challenge (classical + quantum layers)."""

from .engine import analyze, heldout_intervention_prediction
from .generators import simulate
from .quantum_engine import classify_correlations, classify_process
from .quantum_families import apply_family, chsh_data, tomography_data

__all__ = [
    "analyze",
    "heldout_intervention_prediction",
    "simulate",
    "classify_process",
    "classify_correlations",
    "apply_family",
    "tomography_data",
    "chsh_data",
]
