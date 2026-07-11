"""Certificate format for the decoding chain (Discipline Formula v0.2+).

Every benchmark run emits a JSON certificate stating, for each quantity:
FORCED / PERMITTED / FREE / REJECTED, with exact witnesses.
Score = infinity on any violated-or-uncertified hard constraint.

Certificate format v0.3 (R14 / Maudlin M-layer): every certificate MUST
include `m_layer_stipulations` — the un-derived measurement-interface
assumptions the result rests on. See
docs/notes/measurement-interface-maudlin.md.
"""

import json
import time
from typing import Dict, List, Optional, Sequence


def make_certificate(
    problem: str,
    inputs: Dict,
    results: Dict,
    m_layer_stipulations: Optional[Sequence[str]] = None,
    certificate_version: str = "0.3",
) -> Dict:
    hard_ok = all(
        r.get("status") in ("FORCED", "PERMITTED", "PD_CERTIFIED", "PSD_CERTIFIED")
        for r in results.values()
        if isinstance(r, dict) and "status" in r
    )
    stipulations: List[str] = list(m_layer_stipulations) if m_layer_stipulations else []
    if not stipulations:
        stipulations = [
            "UNSPECIFIED — certificate author must list M-layer stipulations "
            "(R14 / certificate format v0.3)"
        ]
    return {
        "certificate_version": certificate_version,
        "problem": problem,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "arithmetic": "exact rational (Fraction); numerics quarantined to atom layer with audited residuals",
        "hard_constraints_certified": hard_ok,
        "score": "finite" if hard_ok else "infinity (violated or uncertified)",
        "m_layer_stipulations": stipulations,
        "inputs": inputs,
        "results": results,
    }


def save_certificate(cert: Dict, path: str) -> None:
    if "m_layer_stipulations" not in cert:
        cert = dict(cert)
        cert["m_layer_stipulations"] = [
            "UNSPECIFIED — certificate author must list M-layer stipulations "
            "(R14 / certificate format v0.3)"
        ]
    with open(path, "w") as f:
        json.dump(cert, f, indent=2)
