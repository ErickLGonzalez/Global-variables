"""B3 discovery pipeline: pseudo-data → relations → d_identifiable certificate."""

from typing import Dict, Optional

from .exact import fmt
from .graph import build_graph
from .pseudo_data import make_closed_system, observed_as_independent
from .rank import d_identifiable, holding_residuals, residuals
from .relations import discover_relations

EXPECTED_BASIS = {"g", "g_prime", "v"}
HEADLINE = {"R1", "R3", "R4", "R5"}


def run_discovery(obs: Optional[Dict] = None) -> Dict:
    if obs is None:
        obs = observed_as_independent(make_closed_system())
    relations = discover_relations(obs)
    graph = build_graph(relations)
    rank_info = d_identifiable(obs)
    names = {r["name"] for r in relations}
    headline_ok = HEADLINE.issubset(names)
    d = rank_info["d_identifiable"]
    free = set(graph["free_sources"])
    preferred = free == EXPECTED_BASIS
    ok = headline_ok and d == 3
    return {
        "status": "PASS" if ok else "FAIL",
        "observed_quantities": {k: fmt(v) for k, v in obs.items()},
        "relations_discovered": relations,
        "headline_relations_found": sorted(HEADLINE & names),
        "headline_complete": headline_ok,
        "dependency_graph": graph,
        "rank_analysis": rank_info,
        "preferred_basis_recovered": preferred,
        "d_identifiable": d,
        "epistemic_summary": {
            "quantities": {
                **{q: "FORCED" for q in graph["forced"]},
                **{q: "FREE" for q in graph["free_sources"]},
            },
            "d_identifiable": d,
            "note": (
                "d_identifiable from exact Jacobian rank over Q; "
                "FREE/FORCED labels from unidirectional template orientation."
            ),
        },
    }


def corrupt(obs: Dict, key: str, factor=None) -> Dict:
    from fractions import Fraction
    out = dict(obs)
    factor = Fraction(11, 10) if factor is None else factor
    out[key] = out[key] * factor
    return out


def broken_relations(obs: Dict) -> list:
    """Names of residuals that fail on corrupted data."""
    return [n for n, r in residuals(obs) if r != 0]
