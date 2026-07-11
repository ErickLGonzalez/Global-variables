"""B5 — cluster decomposition / multi-channel factorization (?5)."""

from .discover import run_discovery
from .pseudo_data import make_factorization_data

__all__ = ["run_discovery", "make_factorization_data"]
