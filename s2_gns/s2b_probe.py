"""S2-b: the exact-kernel GNS probe (fixed operator, varying state).

ERRATUM carried by this module (correcting the S2 addendum): for a SINGLE
interval, the continuum modular Hamiltonian of the chiral fermion vacuum
is purely LOCAL (conformal Bisognano-Wichmann); the Casini-Huerta BILOCAL
terms arise for MULTI-interval regions. The single-interval lattice
mismatch is therefore attributed to the EISLER-PESCHEL long-range lattice
corrections to the local kernel, not to a missing CH term. The CH bilocal
remains the correct object for the future two-interval extension.

S2-b design -- four layers, all with ground truth in hand:

1. KERNEL ANATOMY: the exact lattice kernel K = ln((1-C)/C) is decomposed;
   its nearest-neighbor profile is compared to the continuum local
   prediction K_{i,i+1} ~ -pi * beta(x), beta(x) = x(l-x)/l, and the
   long-range remainder (the EP corrections) is quantified -- the recorded
   reason the geometric local ansatz failed at the Gram level.

2. BOOSTED (coherent/current) ORBIT: states omega_q with
   C_q(j,k) = e^{iq(j-k)} C(j,k) -- the U(1)-boosted Fermi sea, which in
   bosonization is a COHERENT state of the c=1 boson. Exact facts used as
   gates: Delta S(q) = 0 (diagonal unitary; interval spectrum invariant).

3. DUAL-ROUTE RELATIVE ENTROPY: S_rel(omega_q || vac) computed two
   independent ways -- (i) the Gaussian eigen-route
   S_rel = -S(C_rho) - Tr[C_rho ln C_sigma + (1-C_rho) ln (1-C_sigma)],
   and (ii) the modular route Delta<K_exact> - Delta S. Agreement is the
   machinery certificate; quadratic q-scaling is the coherent-state
   signature. The LOCAL ansatz kernel run on the same data quantifies its
   failure under controlled conditions.

4. GRAM-DIAGONAL IDENTITY: capacity of entanglement
   C_E = <(Delta K)^2> = sum_k eps_k^2 nu_k (1 - nu_k)
   must track S itself (2D CFT: capacity = entropy, both (c/3) ln l).
   This is the first verified SECOND-MOMENT (Gram) entry for the fixed
   kernel: omega(K^2) - omega(K)^2 = the entropy slot.
"""

import numpy as np

from .gaussian import ground_state_C, entropy, modular_1p, CLIP


def interval(C, l):
    return C[:l, :l]


def boosted_C(C, q):
    j = np.arange(C.shape[0])
    phase = np.exp(1j * q * (j[:, None] - j[None, :]))
    return C * phase


def kernel_anatomy(l=48):
    """Anatomy finding (corrected in-sprint): the exact kernel's NN
    elements follow the continuum local prediction -pi*beta(x) NEAR THE
    EDGES, then PLATEAU in the bulk while the parabolic weight escapes
    into long-range hoppings (Eisler-Peschel structure). A strictly
    local ansatz is therefore edge-correct and bulk-wrong -- the
    quantified reason it failed at the Gram level."""
    C = interval(ground_state_C(l + 4), l)
    K = modular_1p(C)
    sub = np.array([K[i, i + 1] for i in range(l - 1)])
    # bond (i, i+1) sits at continuum coordinate x = i+1 on [0, l]
    # (half-site offset matters: beta is symmetric about l/2)
    x = np.arange(l - 1) + 1.0
    pred = -np.pi * (x * (l - x) / l)
    edge_idx = [3, 4, 5]
    edge_devs = [abs(sub[i] - pred[i]) / abs(pred[i]) for i in edge_idx]
    mirror = [l - 2 - i for i in edge_idx]
    edge_devs += [abs(sub[i] - pred[i]) / abs(pred[i]) for i in mirror]
    center = (l - 1) // 2
    bulk_ratio = float(sub[center] / pred[center])   # << 1: plateau
    T = np.zeros_like(K)
    for i in range(l):
        for d in (-1, 0, 1):
            if 0 <= i + d < l:
                T[i, i + d] = K[i, i + d]
    lr_fraction = float(np.linalg.norm(K - T) / np.linalg.norm(K))
    third = np.array([K[i, i + 3] for i in range(l - 3)])
    return {"edge_max_dev": float(max(edge_devs)),
            "bulk_NN_over_prediction": bulk_ratio,
            "third_neighbor_bulk": float(third[center - 2]),
            "long_range_frobenius_fraction": lr_fraction}


def gaussian_relative_entropy(C_rho, C_sigma):
    """Exact Gaussian formula (eigen-route)."""
    Cs = (C_sigma + C_sigma.conj().T) / 2
    nu, U = np.linalg.eigh(Cs)
    nu = np.clip(nu, CLIP, 1 - CLIP)
    lnCs = (U * np.log(nu)) @ U.conj().T
    ln1mCs = (U * np.log(1 - nu)) @ U.conj().T
    S_rho = _entropy_c(C_rho)
    cross = -float(np.real(np.trace(C_rho @ lnCs
                                    + (np.eye(len(nu)) - C_rho) @ ln1mCs)))
    return cross - S_rho


def _entropy_c(C):
    nu = np.clip(np.linalg.eigvalsh((C + C.conj().T) / 2), CLIP, 1 - CLIP)
    return float(-np.sum(nu * np.log(nu) + (1 - nu) * np.log(1 - nu)))


def local_ansatz_kernel(l):
    """The geometric LOCAL kernel (the old probe's ansatz), lattice form:
    K_loc[i,i+1] = -pi * beta(i+1/2)."""
    K = np.zeros((l, l))
    for i in range(l - 1):
        x = i + 0.5
        K[i, i + 1] = K[i + 1, i] = -np.pi * x * (l - x) / l
    return K


def orbit_test(l=32, qs=(0.05, 0.10)):
    Cfull = ground_state_C(l + 4)
    C_A = interval(Cfull, l).astype(complex)
    K_ex = modular_1p(np.real(C_A))
    K_lo = local_ansatz_kernel(l)
    out = []
    for q in qs:
        Cq_A = interval(boosted_C(Cfull, q), l)
        dS = _entropy_c(Cq_A) - _entropy_c(C_A)
        srel = gaussian_relative_entropy(Cq_A, C_A)
        dK_ex = float(np.real(np.trace(K_ex @ (Cq_A - C_A))))
        dK_lo = float(np.real(np.trace(K_lo @ (Cq_A - C_A))))
        out.append({"q": q, "dS": dS, "S_rel": srel,
                    "modular_route_exact": dK_ex - dS,
                    "modular_route_local": dK_lo - dS,
                    "dev_exact": abs(dK_ex - dS - srel) / srel,
                    "dev_local": abs(dK_lo - dS - srel) / srel})
    return out


def capacity_vs_entropy(ls=(16, 24, 32, 48, 64)):
    rows = []
    for l in ls:
        C = interval(ground_state_C(l + 4), l)
        nu = np.clip(np.linalg.eigvalsh(C), CLIP, 1 - CLIP)
        eps = np.log((1 - nu) / nu)
        CE = float(np.sum(eps ** 2 * nu * (1 - nu)))
        S = float(-np.sum(nu * np.log(nu) + (1 - nu) * np.log(1 - nu)))
        rows.append({"l": l, "capacity": CE, "entropy": S})
    lo, hi = rows[0], rows[-1]
    slope_CE = (hi["capacity"] - lo["capacity"]) / np.log(hi["l"] / lo["l"])
    slope_S = (hi["entropy"] - lo["entropy"]) / np.log(hi["l"] / lo["l"])
    return rows, slope_CE, slope_S
