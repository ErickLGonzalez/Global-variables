"""B5 discovery pipeline: multi-channel factorization → one coupling."""

from typing import Dict, Optional

from .exact import fmt
from .pseudo_data import make_factorization_data
from .rank import d_identifiable, residuals
from .relations import discover_factorization, factorization_holds

HEADLINE = {"F1", "F3", "F5"}


def run_discovery(obs: Optional[Dict] = None) -> Dict:
    if obs is None:
        obs = make_factorization_data()
    relations = discover_factorization(obs)
    names = {r["name"] for r in relations}
    # F4_* collapse counts as headline channel-equality
    f4_ok = any(n.startswith("F4_") for n in names)
    headline_ok = HEADLINE.issubset(names) and f4_ok and factorization_holds(obs)
    rank_info = d_identifiable(obs)
    d = rank_info["d_identifiable"]
    ok = headline_ok and d == 1
    forced = sorted({r["output"] for r in relations})
    free = ["alpha_22"] if d == 1 else []
    return {
        "status": "PASS" if ok else "FAIL",
        "observed_quantities": {k: fmt(v) for k, v in obs.items()},
        "relations_discovered": relations,
        "headline_complete": headline_ok,
        "rank_analysis": rank_info,
        "d_identifiable": d,
        "free_sources": free,
        "forced_quantities": forced,
        "composition_claim": (
            "One coupling governs all factorization channels "
            "(cluster decomposition / locality → Cmp column = H)."
        ),
    }


def broken_residuals(obs: Dict) -> list:
    return [n for n, r in residuals(obs) if r != 0]
