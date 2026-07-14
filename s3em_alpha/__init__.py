"""S3-EM — fine-structure constant consistency layer (EXP-D)."""

from .analysis import (
    CHANNELS,
    codata_expansion_view,
    consistency_report,
    jackknife,
    localization,
    weighted_mean,
)

__all__ = [
    "CHANNELS",
    "consistency_report",
    "jackknife",
    "localization",
    "codata_expansion_view",
    "weighted_mean",
]
