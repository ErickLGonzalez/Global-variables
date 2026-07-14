"""M2 -- typed candidate generator ('infer' machine).

Emits candidate LAWS y = f(x_1..x_n) drawn from a bounded typed grammar,
scored against measured tables by fit residual + MDL complexity penalty.
Candidates are canonicalized via M1 (spectrum/signature hashing on their
linearized-around-mean Jacobian) so equivalent-up-to-reparametrization
laws collapse to ONE representative -- the deduplication that makes the
search space finite.

Typed grammar (this sprint, sufficient for B3/B5 rediscovery):
  primitives   x_i, constants c_k
  operators    (a*b), (a/b), (a^p) with p in a small integer/half set
  law shape    y = c * prod_i x_i ^ p_i             (monomial family)
Each candidate is a tuple of integer/half-integer exponents plus one
free multiplicative constant, fit by log-linear regression when all
inputs positive. Complexity = number of nonzero exponents. MDL score =
n * ln(RSS/n) + k * ln(n).

This is deliberately narrow: monomial power laws cover B3 (Fermi's
constant from e, M_W, s_W) and B5 (R_24 = A_22^2). Wider grammars
(polynomials, trig, differential invariants) are M2-b's target with the
same interface -- verifiers and canonicalization untouched.
"""

from itertools import product
from typing import Callable, Iterable, List, Tuple

import numpy as np


def enumerate_monomials(n_inputs: int, exponents: Iterable = (-2, -1,
                                                              -0.5, 0.5,
                                                              1, 2),
                        max_nonzero: int = 4):
    """All exponent tuples in the allowed set with at most max_nonzero
    nonzero entries (implicit constant handled outside)."""
    exps = list(exponents)
    seen = set()
    for combo in product([0] + exps, repeat=n_inputs):
        if sum(int(e != 0) for e in combo) > max_nonzero:
            continue
        if all(e == 0 for e in combo):
            continue
        seen.add(combo)
    return list(seen)


def fit_monomial(X: np.ndarray, y: np.ndarray, exps: Tuple[float, ...]):
    """Fit y = c * prod_i x_i^{e_i}: log-linear regression for ln c."""
    logX = np.log(X)
    pred_log = logX @ np.asarray(exps)
    logy = np.log(y)
    lnc = float(np.mean(logy - pred_log))
    resid = logy - (pred_log + lnc)
    rss = float(np.sum(resid ** 2))
    return {"lnc": lnc, "c": float(np.exp(lnc)),
            "rss_log": rss, "n": len(y),
            "rel_log_residual": float(np.sqrt(rss / len(y)))}


def mdl_score(fit, k_nonzero):
    n = fit["n"]
    return n * np.log(fit["rss_log"] / n + 1e-30) + k_nonzero * np.log(n)


def canonical_signature(exps, lnc, quant=1e-4):
    """R15/M1-flavored signature: sorted rounded exponent multiset +
    quantized ln(c). Reparametrization ambiguities (e.g. rescaling one
    input) shift lnc but leave the exponent multiset invariant; grouping
    by multiset alone reveals the true 'same law' class."""
    ms = tuple(sorted(round(e * 2) / 2 for e in exps if e != 0))
    return {"exponent_multiset": ms,
            "lnc_quantized": round(lnc / quant) * quant}


def search(X: np.ndarray, y: np.ndarray, feature_names: List[str],
           exponents=(-2, -1, -0.5, 0.5, 1, 2), max_nonzero: int = 4):
    """Return top candidates by MDL, one per canonical exponent multiset.
    Deduplication is the point: the raw search emits many laws; canonical
    grouping keeps ONE representative per equivalence class."""
    assert (X > 0).all() and (y > 0).all(), \
        "monomial regressor requires positive data"
    cands = []
    for exps in enumerate_monomials(X.shape[1], exponents, max_nonzero):
        f = fit_monomial(X, y, exps)
        k = sum(int(e != 0) for e in exps)
        cands.append({"exponents": exps, "fit": f, "k_nonzero": k,
                      "mdl": mdl_score(f, k),
                      "canonical": canonical_signature(exps, f["lnc"])})
    # dedupe by exponent multiset -- keep the minimum-MDL representative
    by_class = {}
    for c in cands:
        key = c["canonical"]["exponent_multiset"]
        if key not in by_class or c["mdl"] < by_class[key]["mdl"]:
            by_class[key] = c
    ranked = sorted(by_class.values(), key=lambda r: r["mdl"])
    return ranked, {"n_raw": len(cands), "n_classes": len(by_class),
                    "feature_names": feature_names,
                    "verifier_hook": "hand top-k to any certified "
                                     "verifier (B1/B2/B3/B6/B10); this "
                                     "layer only PROPOSES"}
