"""S2 — GNS realization probe for conjecture ?2 (free-fermion route)."""

from .chain import (
    current_carrying_correlation,
    thermal_correlation,
    vacuum_correlation,
)
from .continuum import coherent_pivot_split, vacuum_gram_rank1
from .probe import (
    calibrate_vacuum,
    connected_gram_region,
    continuum_vacuum_M,
    cut_stress_excess,
    fit_c_over_3,
    probe_matrix,
)

from .gaussian import (
    ground_state_C,
    modular_1p,
    thermal_C,
    validity_gate,
)
from .qnec_lattice import thermal_identity_report, vacuum_saturation_report

__all__ = [
    "vacuum_correlation",
    "thermal_correlation",
    "current_carrying_correlation",
    "calibrate_vacuum",
    "probe_matrix",
    "fit_c_over_3",
    "continuum_vacuum_M",
    "vacuum_gram_rank1",
    "coherent_pivot_split",
    "ground_state_C",
    "thermal_C",
    "modular_1p",
    "validity_gate",
    "vacuum_saturation_report",
    "thermal_identity_report",
]
