"""Certificate format for the decoding chain (Discipline Formula v0.2).

Every B1 run emits a JSON certificate stating, for each quantity:
FORCED / PERMITTED / FREE / REJECTED, with exact witnesses.
Score = infinity on any violated-or-uncertified hard constraint.
"""

import json
import time
from typing import Dict


def make_certificate(problem: str, inputs: Dict, results: Dict) -> Dict:
    hard_ok = all(
        r.get("status") in ("FORCED", "PERMITTED", "PD_CERTIFIED", "PSD_CERTIFIED")
        for r in results.values()
        if isinstance(r, dict) and "status" in r
    )
    return {
        "certificate_version": "0.2",
        "problem": problem,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "arithmetic": "exact rational (Fraction); numerics quarantined to atom layer with audited residuals",
        "hard_constraints_certified": hard_ok,
        "score": "finite" if hard_ok else "infinity (violated or uncertified)",
        "inputs": inputs,
        "results": results,
    }


def save_certificate(cert: Dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(cert, f, indent=2)
