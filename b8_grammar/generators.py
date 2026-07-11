"""B8 data generators: trajectories from KNOWN structural grammars, labels
hidden from the identifier.

Linear dynamical grammars, dz/dt = A z with A = -(M + W) K:
  HAMILTONIAN     M = 0,  W antisymmetric != 0   (conservative)
  GRADIENT_FLOW   W = 0,  M SPD                  (pure dissipation)
  GENERIC_MIXED   M SPD and W antisymmetric      (dissipative + conservative)
with K SPD (quadratic potential V = z^T K z / 2).

Chart-free invariant signature (canonicalization rule, R15 addendum):
the spectrum of A is similarity-invariant. For stable linear systems:
  HAMILTONIAN     spectrum purely imaginary, +/- i omega pairs
  GRADIENT_FLOW   spectrum real and negative (A similar to -sqrt(K) M sqrt(K))
  GENERIC_MIXED   complex eigenvalues with strictly negative real parts
Weak damping is spectrally close to Hamiltonian -> the identifier MUST
return AMBIGUOUS there rather than force a choice.

Quantum grammars (exact, reuse B2): a process's Choi matrix J with
  UNITARY_GRAMMAR      J PSD, TP, rank 1
  DISSIPATIVE_CPTP     J PSD, TP, rank > 1
  NOT_A_CHANNEL        J not PSD (or not TP)
"""

import numpy as np


def _expm_traj(A, z0, dt, n_steps, rng=None, obs_noise=0.0):
    from scipy.linalg import expm
    P = expm(A * dt)
    zs = [np.asarray(z0, float)]
    for _ in range(n_steps):
        zs.append(P @ zs[-1])
    Z = np.stack(zs)
    if obs_noise > 0 and rng is not None:
        Z = Z + obs_noise * rng.standard_normal(Z.shape)
    return Z


def make_A(grammar, k=(3.0, 1.0), m=(0.6, 0.9), w=1.0, damping=None):
    K = np.diag(k)
    W = np.array([[0.0, w], [-w, 0.0]])
    M = np.diag(m)
    if grammar == "HAMILTONIAN":
        return -(W) @ K
    if grammar == "GRADIENT_FLOW":
        return -(M) @ K
    if grammar == "GENERIC_MIXED":
        return -(M + W) @ K
    if grammar == "WEAK_DAMPING":  # near-Hamiltonian: honest AMBIGUOUS target
        eps = damping if damping is not None else 1e-4
        return -(eps * np.eye(2) + W) @ K
    raise ValueError(grammar)


def trajectories(grammar, n_traj=20, n_steps=400, dt=0.01, seed=0,
                 obs_noise=1e-3, **kw):
    rng = np.random.default_rng(seed)
    A = make_A(grammar, **kw)
    return [_expm_traj(A, rng.standard_normal(2), dt, n_steps, rng, obs_noise)
            for _ in range(n_traj)], A


# ---- exact quantum channels (labels hidden from identifier) --------------

def quantum_instance(kind):
    from b2_process_solver.choi import (pythagorean_unitary,
                                        identity_channel, z_channel, mix)
    from b2_process_solver.cexact import CF
    from fractions import Fraction as F
    if kind == "UNITARY":
        return pythagorean_unitary()
    if kind == "DISSIPATIVE":
        return mix([(identity_channel(), F(2, 3)), (z_channel(), F(1, 3))])
    if kind == "FAKE":
        J = pythagorean_unitary()
        J = [[CF(J[i][j].re, J[i][j].im) for j in range(4)] for i in range(4)]
        J[2][2] = CF(F(-1, 50))
        return J
    raise ValueError(kind)
