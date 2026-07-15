"""Stage 5 / coverage.py: block x predicate coverage matrix, saturation report,
admission-rule evaluation, and falsifier liveness computation (Stage 2 rule).

Liveness rule (Survey Rec-2): a falsifier is 'live' iff required capability is
within one order of magnitude of current capability. 'witness_search' falsifiers
are live by definition (a single witness decides). 'already_decisive' are closed.
"""
from __future__ import annotations
import json
import math
import os
from collections import defaultdict
from .common import make_certificate, load_json, DATA_DIR

PREDICATES = ["Sym", "Pos", "Uni", "Cau", "Cmp", "RG", "Top", "Thm"]


def falsifier_liveness(f):
    d = f.get("direction")
    if d == "witness_search":
        return "live"
    if d == "already_decisive":
        return "closed_decisive"
    req = f["required_capability"]["value"]
    cur = f["current_capability"]["value"]
    if req is None or cur is None or req <= 0 or cur <= 0:
        return "indeterminate"
    gap = abs(math.log10(cur / req))
    return "live" if gap <= 1.0 else f"latent (gap {gap:.1f} OOM)"


def run():
    ledger = load_json(DATA_DIR, "ledger.json")
    falsifiers = load_json(DATA_DIR, "falsifiers.json")

    # --- coverage matrix ---
    matrix = defaultdict(list)
    predicate_counts = defaultdict(int)
    for e in ledger["entries"]:
        for block in e["blocks"]:
            for pred in e["predicates"]:
                matrix[f"{block}|{pred}"].append(e["label"])
        for pred in e["predicates"]:
            predicate_counts[pred] += 1

    scarce = [p for p in PREDICATES if predicate_counts[p] <= 2]
    saturated_cells = {cell: labels for cell, labels in matrix.items() if len(labels) >= 3}

    # --- Stage-4 audit: contested entries must carry a reason ---
    untagged_contested = [e["label"] for e in ledger["entries"]
                          if e["contested"] and not e.get("contested_reason")]

    # --- Stage-2: falsifier liveness + linkage audit ---
    liveness = {f["id"]: falsifier_liveness(f) for f in falsifiers["falsifiers"]}
    falsifier_entries = {f["entry_id"] for f in falsifiers["falsifiers"]}
    bidirectional_unlinked = [
        e["label"] for e in ledger["entries"]
        if e["bidirectional"] and not e.get("falsifier_ids")
        and e["entry_id"] not in falsifier_entries]

    # --- admission-rule statement (Survey Rec-5) ---
    admission_rule = ("ADMIT new entry iff it (a) touches a block x predicate cell with "
                      "< 3 current entries, or (b) supplies a new compute hook "
                      "(pipeline) for an existing cell. Otherwise DEPRIORITIZE.")

    verdict_bits = []
    verdict_bits.append("Uni-column scarcity CONFIRMED" if "Uni" in scarce
                        else "Uni-column adequately covered")
    verdict_bits.append("Stage-4 audit PASS" if not untagged_contested
                        else f"Stage-4 audit FAIL: {untagged_contested}")
    verdict_bits.append("falsifier linkage PASS" if not bidirectional_unlinked
                        else f"falsifier linkage GAPS: {bidirectional_unlinked}")

    return make_certificate(
        pipeline="coverage", entry_id="cdl-rh-grh",  # meta-cert; nominal entry anchor
        soundness_tag="SOUND",
        stipulations=[{"name": "liveness_rule",
                       "assumed": "within 1 OOM = live", "source": "Survey Rec-2"}],
        inputs={"n_entries": len(ledger["entries"]),
                "n_falsifiers": len(falsifiers["falsifiers"])},
        verdict="; ".join(verdict_bits),
        verdict_detail={
            "predicate_counts": dict(predicate_counts),
            "scarce_predicates": scarce,
            "saturated_cells": saturated_cells,
            "falsifier_liveness": liveness,
            "bidirectional_entries_without_falsifiers": bidirectional_unlinked,
            "admission_rule": admission_rule,
        },
        notes="Meta-certificate over the ledger, not over a physical/mathematical claim.",
    )


if __name__ == "__main__":
    cert = run()
    print(json.dumps(cert, indent=2))
