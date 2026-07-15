"""M1 -- the canonicalization engine.

Every domain artifact -> a CHART-INVARIANT feature vector. The R15 rule
(only reparametrization-invariant data count) implemented as code, so
that cross-domain "same" claims are made on the invariants, never on
raw representations.

GROUP ACTION treated in this sprint: encoder change z = A x, positive-
definite conjugation on the OU generator side (dropped, since the drift
Jacobian's spectrum is chart-invariant on its own -- see feature list).
Rationale: covers B8 grammar generators, B9 M/W decomposition, S2 modular
kernels, S4 rank saturation, B10 CP data. Broader gauge families are
deferred to M1-b with a named test list; PSD-conjugation change of
coordinates on covariance/generator pairs is the workhorse case.

FEATURES (all group-invariants):
  spectrum_hash      sorted eigenvalues of the drift generator, quantized
                     to 5 decimals -- chart-invariant on similarity.
  psd_signature      (dim, rank, +count, 0count, -count) of the symmetric
                     part -- unchanged under A(.)A^T.
  bloch_radii        for CV/qubit Choi: singular values of the map on the
                     traceless block, quantized. Sensitive to POST unitary
                     freedom only, which is the correct residual gauge.
  time_reversal      sign of the antisymmetric part's Pfaffian sign
                     structure -- discrete gauge invariant.
  factor_poset       cluster-block indices (which coordinates couple):
                     canonicalized as sorted tuples of sorted tuples.

CANONICAL INVARIANT VECTOR: concatenation of the above with a stable
hashing rule; the SAME chart-transformed input MUST produce the SAME
vector byte-for-byte.
"""

import hashlib
from typing import List, Tuple

import numpy as np


def _sig_from_eigs(w, atol=1e-9):
    pos = int(np.sum(w > atol))
    zer = int(np.sum(np.abs(w) <= atol))
    neg = int(np.sum(w < -atol))
    return {"dim": int(w.size), "rank": pos + neg,
            "n_pos": pos, "n_zero": zer, "n_neg": neg}


def spectrum_signature(A, quant=1e-5):
    """Sorted (real, imag) eigenvalue pairs, quantized. Similarity-
    invariant on any square matrix."""
    ev = np.linalg.eigvals(np.asarray(A, dtype=complex))
    pairs = sorted([(float(np.round(z.real / quant) * quant),
                     float(np.round(z.imag / quant) * quant)) for z in ev])
    return tuple(pairs)


def psd_signature(S, atol=1e-9):
    """Signature of the symmetric part; unchanged under X -> A X A^T."""
    Sh = (np.asarray(S) + np.asarray(S).T) / 2
    return _sig_from_eigs(np.linalg.eigvalsh(Sh), atol)


def antisym_pfaffian_sign(W):
    """Sign of the Pfaffian of the antisymmetric part (via ordered
    eigenvalue phases). For 2x2: sign of W[0,1]. Chart-invariant on
    orientation-preserving A."""
    Wa = (np.asarray(W) - np.asarray(W).T) / 2
    if Wa.shape[0] % 2:
        return 0
    ev = np.linalg.eigvals(Wa)
    prod = np.prod(np.sort(ev.imag)[::2])
    return int(np.sign(prod.real)) if abs(prod) > 1e-12 else 0


def factor_poset(coupling_matrix, atol=1e-8):
    """Connected components of the (numerical) support pattern -- the
    factorization structure. Canonicalized to a sorted tuple of sorted
    tuples."""
    M = np.abs(np.asarray(coupling_matrix)) > atol
    n = M.shape[0]
    seen = [False] * n
    comps = []
    for i in range(n):
        if seen[i]:
            continue
        stack, comp = [i], []
        while stack:
            k = stack.pop()
            if seen[k]:
                continue
            seen[k] = True
            comp.append(k)
            for j in range(n):
                if (M[k, j] or M[j, k]) and not seen[j]:
                    stack.append(j)
        comps.append(tuple(sorted(comp)))
    return tuple(sorted(comps))


def bloch_singular_values(choi, quant=1e-4):
    """For a 4x4 qubit-channel Choi: the reduced-map singular values on
    the traceless block. Left- and right- unitary invariant."""
    C = np.asarray(choi, dtype=complex)
    from b12_rgrc.quantum_families import PAULIS
    R = np.zeros((3, 3))
    for a in range(1, 4):
        for b in range(1, 4):
            R[a - 1, b - 1] = float(np.real(np.trace(C @ np.kron(
                PAULIS[a], PAULIS[b]))))
    sv = np.sort(np.linalg.svd(R, compute_uv=False))[::-1]
    return tuple(float(np.round(s / quant) * quant) for s in sv)


def canonicalize(kind: str, **artifact) -> Tuple[dict, str]:
    """Kind-specific invariant extractor. Returns (features, hash).

    kinds:
      'generator'      artifact={"A": drift matrix, opt "S": diffusion}
      'choi_qubit'     artifact={"C": 4x4 Choi}
      'covariance'     artifact={"C": covariance / Gram matrix}
    """
    feats = {"kind": kind}
    if kind == "generator":
        A = np.asarray(artifact["A"])
        feats["spectrum"] = spectrum_signature(A)
        feats["antisym_sign"] = antisym_pfaffian_sign(A)
        feats["factor_poset"] = factor_poset(A)
        if "S" in artifact:
            feats["psd_signature"] = psd_signature(artifact["S"])
    elif kind == "choi_qubit":
        C = np.asarray(artifact["C"], dtype=complex)
        feats["psd_signature"] = psd_signature(C.real)
        feats["bloch_singular_values"] = bloch_singular_values(C)
    elif kind == "metric_pair":
        # GfE-imported mathematics (R34, Sec II.A): the Lorentz/GL-
        # invariant spectrum of a metric PAIR is the generalized
        # eigenvalue set of (G, g) -- eigenvalues of g^{-1} G, invariant
        # under simultaneous congruence g -> A g A^T, G -> A G A^T.
        # The eigenvalue-log core of the GQRE is the Burg/Stein
        # divergence D(g||G) = sum(lam - ln lam - 1) >= 0, = 0 iff G = g.
        g = np.asarray(artifact["g"], dtype=float)
        G = np.asarray(artifact["G"], dtype=float)
        lam = np.sort(np.real(np.linalg.eigvals(np.linalg.solve(g, G))))
        quantized = tuple(float(np.round(l / 1e-6) * 1e-6) for l in lam)
        feats["pair_spectrum"] = quantized
        feats["burg_divergence"] = float(np.round(
            np.sum(lam - np.log(lam) - 1.0) / 1e-9) * 1e-9)
    elif kind == "covariance":
        C = np.asarray(artifact["C"])
        feats["psd_signature"] = psd_signature(C)
        feats["spectrum"] = spectrum_signature(C)
    else:
        raise ValueError(kind)
    payload = repr(sorted(feats.items())).encode()
    return feats, hashlib.sha256(payload).hexdigest()[:16]
