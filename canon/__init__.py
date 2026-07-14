"""M1 — Canonicalization engine (chart-invariant feature extraction)."""

from .engine import (
    antisym_pfaffian_sign,
    bloch_singular_values,
    canonicalize,
    factor_poset,
    psd_signature,
    spectrum_signature,
)

__all__ = [
    "canonicalize",
    "spectrum_signature",
    "psd_signature",
    "antisym_pfaffian_sign",
    "factor_poset",
    "bloch_singular_values",
]
