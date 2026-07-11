"""Exact helpers for Onsager transport-matrix completion (B7)."""

from fractions import Fraction
from typing import List, Optional

Q = Fraction


def q(x) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


def fmt(x: Fraction) -> str:
    return str(q(x))


Mat = List[List[Optional[Fraction]]]
