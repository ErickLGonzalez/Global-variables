"""B12-RGRC — Rival-grammar recovery challenge (shared-latent discrimination)."""

from .engine import analyze, heldout_intervention_prediction
from .generators import simulate

__all__ = [
    "analyze",
    "heldout_intervention_prediction",
    "simulate",
]
