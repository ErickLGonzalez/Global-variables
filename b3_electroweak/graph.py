"""Dependency graph labels (FREE / FORCED) from unidirectional templates.

d_identifiable itself is computed in rank.py via Jacobian rank; this
module only provides the epistemic labeling for the certificate.
"""

from collections import defaultdict
from typing import Dict, Iterable, List, Tuple

ALL_Q = [
    "g", "g_prime", "v", "sin_theta_W", "cos_theta_W",
    "e", "M_W", "M_Z", "G_F_inv_sq",
]

# Relations that are bidirectional constraints / not a unique force onto
# a preferred free basis member. We still record them, but do not mark
# their `output` as FORCED when that would eat the canonical free set.
# R7 is a pure constraint. R8 can express g from angles — keep g FREE by
# not treating R8 as producing a forced source.
NON_FORCING = {"R8"}


def build_graph(relations: Iterable[Dict]) -> Dict:
    relations = list(relations)
    forcing = [r for r in relations if r["name"] not in NON_FORCING]
    constraints = [r for r in relations if r["name"] in NON_FORCING]

    produced: Dict[str, List[Dict]] = defaultdict(list)
    edges: List[Tuple[str, str]] = []
    for r in forcing:
        out = r["output"]
        produced[out].append(r)
        for inp in r["inputs"]:
            edges.append((inp, out))

    forced = set(produced.keys())
    free = [q for q in ALL_Q if q not in forced]

    return {
        "edges": [{"from": a, "to": b} for a, b in edges],
        "forced": sorted(forced),
        "free_sources": sorted(free),
        "forcing_relations": [r["name"] for r in forcing],
        "constraints": [r["name"] for r in constraints],
        "production": {k: [r["name"] for r in v] for k, v in produced.items()},
    }
