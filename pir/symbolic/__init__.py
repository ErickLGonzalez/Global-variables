"""Symbolic constraint bridge (Stage 2 / P4): exact-rational feasibility with
SAT witnesses and Farkas/UNSAT certificates, lowered into PIR facts."""

from . import bridge, linear
from .bridge import constraint_fact
from .linear import solve, verify_farkas, verify_null, verify_solution

__all__ = ["bridge", "linear", "constraint_fact", "solve",
           "verify_farkas", "verify_null", "verify_solution"]
