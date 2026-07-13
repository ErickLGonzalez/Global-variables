"""B12-b: the quantum layer of the rival-grammar recovery challenge.

Process families (single qubit, ground truth hidden from the engine):
  G1 QUANTUM_CPTP        unitary (Hadamard-axis rotation) + weak
                         depolarizing: Choi PSD, TP, coherence-preserving.
  G2 CLASSICAL_EMBEDDABLE stochastic matrix on populations + full
                         dephasing: CPTP but diagonal -- a classical
                         process wearing quantum clothes.
  G3 BEYOND_QUANTUM      transpose composed with mild depolarizing:
                         POSITIVE (every single-system output is a valid
                         state) but NOT completely positive -- fails
                         exactly under composition with an ancilla. The
                         Cmp column is the discriminator.
  G4 NOT_A_PROCESS       a non-positive map: produces negative 'states'.

Correlation families (CHSH ladder):
  C1 LHV mixture (S ~ 1.8) | C2 singlet at optimal angles (S ~ 2.83)
  | C3 PR box (S ~ 3.9 sampled). Gates: classical bound 2, Tsirelson
  bound 2*sqrt(2), algebraic bound 4.
"""

import numpy as np

I2 = np.eye(2, dtype=complex)
SX = np.array([[0, 1], [1, 0]], dtype=complex)
SY = np.array([[0, -1j], [1j, 0]], dtype=complex)
SZ = np.array([[1, 0], [0, -1]], dtype=complex)
PAULIS = [I2, SX, SY, SZ]


def apply_family(fam, rho):
    if fam == "G1":
        th = 0.9
        U = np.cos(th / 2) * I2 - 1j * np.sin(th / 2) * (SX + SZ) / np.sqrt(2)
        out = U @ rho @ U.conj().T
        return 0.92 * out + 0.08 * np.trace(rho) * I2 / 2
    if fam == "G2":
        p = np.real(np.diag(rho))
        S = np.array([[0.8, 0.3], [0.2, 0.7]])
        q = S @ p
        return np.diag(q).astype(complex)
    if fam == "G3":
        out = rho.T
        return 0.85 * out + 0.15 * np.trace(rho) * I2 / 2
    if fam == "G4":
        # trace-preserving but NOT positive: overshoots the Bloch ball
        out = 1.5 * (rho - np.trace(rho) * I2 / 2) + np.trace(rho) * I2 / 2
        return out
    raise ValueError(fam)


def choi(fam):
    """Choi state (Lambda x id)|Phi+><Phi+| = (1/2) sum L(|i><j|) x |i><j|."""
    C = np.zeros((4, 4), dtype=complex)
    for i in range(2):
        for j in range(2):
            E = np.zeros((2, 2), dtype=complex)
            E[i, j] = 1.0
            C += np.kron(apply_family(fam, E), E) / 2
    return C


def tomography_data(fam, n_shots=200_000, seed=0, access="full"):
    """Noisy Choi reconstruction: 16 two-qubit Pauli expectations of the
    Choi state, each with shot noise 1/sqrt(n). access='populations'
    zeroes out every expectation involving coherences (X or Y on the
    input side AND output side blocks) -- the apparatus-limited regime."""
    rng = np.random.default_rng(seed)
    C = choi(fam)
    ex = {}
    for a, P in enumerate(PAULIS):
        for b, Q in enumerate(PAULIS):
            val = float(np.real(np.trace(C @ np.kron(P, Q))))
            noisy = val + rng.standard_normal() / np.sqrt(n_shots)
            if access == "populations" and (a in (1, 2) or b in (1, 2)):
                noisy = None                     # unobservable
            ex[(a, b)] = noisy
    return ex


def reconstruct_choi(ex):
    C = np.zeros((4, 4), dtype=complex)
    known = 0
    for (a, b), v in ex.items():
        if v is None:
            continue
        known += 1
        C += v * np.kron(PAULIS[a], PAULIS[b]) / 4
    return C, known


def chsh_data(fam, n_per_setting=40_000, seed=0):
    rng = np.random.default_rng(seed)
    if fam == "C1":
        E = {(0, 0): 0.45, (0, 1): 0.45, (1, 0): 0.45, (1, 1): -0.45}
    elif fam == "C2":
        v = 1 / np.sqrt(2)
        E = {(0, 0): v, (0, 1): v, (1, 0): v, (1, 1): -v}
    else:                                        # C3 PR box
        E = {(0, 0): 0.98, (0, 1): 0.98, (1, 0): 0.98, (1, 1): -0.98}
    out = {}
    for k, e in E.items():
        p_agree = (1 + e) / 2
        agree = rng.binomial(n_per_setting, p_agree)
        out[k] = (2 * agree / n_per_setting - 1, n_per_setting)
    return out
