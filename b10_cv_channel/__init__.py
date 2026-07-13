"""B10 — Continuous-variable Gaussian-channel completion (EXP-A back-end)."""

from .gaussian_channel import (
    certify_channel,
    cp_matrix,
    force_symplectic_entry,
    matmul_r,
    omega,
    permitted_noise_interval,
    transpose,
)

__all__ = [
    "omega",
    "matmul_r",
    "transpose",
    "cp_matrix",
    "certify_channel",
    "permitted_noise_interval",
    "force_symplectic_entry",
]
