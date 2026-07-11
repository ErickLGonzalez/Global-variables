"""Exact algebraic helpers for the electroweak closed system.

All claims use Fraction arithmetic. The Weinberg angle is a Pythagorean
rational (sin, cos) so trig identities stay exact. The G_F relation
involves √2; we certify it via the squared identity
    1/(G_F² v⁴) = 2
which is exact-rational, and report the unsquared form as the discovered
physics relation.
"""

from fractions import Fraction
from typing import Dict, Iterable, Tuple


Q = Fraction


def q(x) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


def isqrt_exact(n: Fraction) -> Fraction:
    """Exact rational square root, or raise if not a perfect square in Q."""
    n = q(n)
    if n < 0:
        raise ValueError("negative")
    # n = a/b in lowest terms; need both a,b perfect squares
    a, b = n.numerator, n.denominator
    sa, sb = _isqrt_int(a), _isqrt_int(b)
    if sa * sa != a or sb * sb != b:
        raise ValueError(f"not a perfect square in Q: {n}")
    return Fraction(sa, sb)


def _isqrt_int(n: int) -> int:
    if n < 0:
        raise ValueError
    if n < 2:
        return n
    x = 1 << ((n.bit_length() + 1) // 2)
    while True:
        y = (x + n // x) // 2
        if y >= x:
            return x
        x = y


def pythagorean_angle(a: int = 3, b: int = 4) -> Tuple[Fraction, Fraction]:
    """Return (sin θ, cos θ) as exact rationals from a Pythagorean pair."""
    a, b = abs(a), abs(b)
    c = _isqrt_int(a * a + b * b)
    if c * c != a * a + b * b:
        raise ValueError("not Pythagorean")
    return Fraction(a, c), Fraction(b, c)


def fmt(x: Fraction) -> str:
    return str(q(x))
