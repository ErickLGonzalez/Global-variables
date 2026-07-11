"""Exact helpers for the B5 cluster / factorization benchmark."""

from fractions import Fraction
from typing import Dict

Q = Fraction


def q(x) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


def fmt(x: Fraction) -> str:
    return str(q(x))
