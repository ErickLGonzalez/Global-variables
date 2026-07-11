"""B7 — Onsager transport-matrix completion (L ⪰ 0 + reciprocity)."""

from .complete import audit_full, force_by_reciprocity, permitted_offdiag
from .pseudo_data import thermoelectric_L

__all__ = [
    "thermoelectric_L",
    "audit_full",
    "force_by_reciprocity",
    "permitted_offdiag",
]
