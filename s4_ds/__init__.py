"""S4 — ?7 toy: dS2 static-patch Gram rank saturation."""

from .kernel import (
    compression_certificate,
    effective_rank,
    precision_audit,
    redshift_profile,
    saturation_curve,
    thermal_kernel_fast,
    weighted_gram,
)

__all__ = [
    "thermal_kernel_fast",
    "redshift_profile",
    "weighted_gram",
    "effective_rank",
    "saturation_curve",
    "compression_certificate",
    "precision_audit",
]
