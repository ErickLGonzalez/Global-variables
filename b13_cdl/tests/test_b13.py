"""B13-CDL headless test harness (blueprint-B1 pattern).

Runs: schema validation of ledger + falsifiers, all seven pipelines, certificate
schema validation, coverage meta-certificate. Exit nonzero on any failure.

Usage:  python3 tests/test_b13.py
"""
from __future__ import annotations
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cdl import common
from src.cdl import (ew_vacuum, strong_cp, varying_constants,
                     grh_miller, tunnell_bsd, muon_g2, h0_tension, coverage)

FAILURES = []


def check(label, errors):
    if errors:
        FAILURES.append((label, errors))
        print(f"  [FAIL] {label}")
        for e in errors[:8]:
            print(f"         - {e}")
    else:
        print(f"  [ ok ] {label}")


def main():
    print("== B13-CDL test harness ==")

    # 1. Ledger validates against entry schema
    entry_schema = common.load_json(common.SCHEMA_DIR, "cdl_entry.schema.json")
    ledger = common.load_json(common.DATA_DIR, "ledger.json")
    errs = []
    for e in ledger["entries"]:
        errs.extend(common.validate(e, entry_schema, f"$.{e.get('label','?')}"))
    check(f"ledger schema ({len(ledger['entries'])} entries)", errs)

    # 2. Falsifier linkage sanity
    falsifiers = common.load_json(common.DATA_DIR, "falsifiers.json")
    entry_ids = {e["entry_id"] for e in ledger["entries"]}
    errs = [f"falsifier {f['id']} references unknown entry {f['entry_id']}"
            for f in falsifiers["falsifiers"] if f["entry_id"] not in entry_ids]
    fal_ids = {f["id"] for f in falsifiers["falsifiers"]}
    for e in ledger["entries"]:
        for fid in e.get("falsifier_ids", []):
            if fid not in fal_ids:
                errs.append(f"entry {e['label']} references unknown falsifier {fid}")
    check(f"falsifier cross-links ({len(falsifiers['falsifiers'])} falsifiers)", errs)

    # 3. Run pipelines, validate certificates, write them
    cert_schema = common.load_json(common.SCHEMA_DIR, "cdl_certificate.schema.json")
    pipelines = [("ew_vacuum", ew_vacuum.run), ("strong_cp", strong_cp.run),
                 ("varying_constants", varying_constants.run),
                 ("grh_miller", grh_miller.run), ("tunnell_bsd", tunnell_bsd.run),
                 ("muon_g2", muon_g2.run), ("h0_tension", h0_tension.run),
                 ("coverage", coverage.run)]
    for name, fn in pipelines:
        try:
            cert = fn()
            errs = common.validate(cert, cert_schema, f"$({name})")
            check(f"pipeline {name} -> {cert['verdict'][:64]}", errs)
            if not errs:
                path = common.write_certificate(cert)
                print(f"         cert: {os.path.relpath(path, common.PKG_ROOT)}")
        except Exception as exc:  # noqa: BLE001 — harness must report, not crash
            check(f"pipeline {name}", [f"exception: {exc!r}"])

    # 4. Domain-specific invariants
    tb = tunnell_bsd.run()
    check("tunnell cross-check vs known table",
          [] if tb["verdict_detail"]["cross_check_vs_known_table"] == "PASS"
          else ["known congruent-number table mismatch"])

    gm = grh_miller.run()
    comp_rows = [r for r in gm["verdict_detail"]["results"] if "COMPOSITE" in r["verdict"]]
    check("miller composite rows carry witnesses",
          [] if all(r["witness_base"] is not None for r in comp_rows)
          else ["missing composite witness"])

    print("\n== SUMMARY ==")
    if FAILURES:
        print(f"FAIL: {len(FAILURES)} check(s) failed.")
        sys.exit(1)
    print("PASS: all checks green. Certificates in certificates/.")
    sys.exit(0)


if __name__ == "__main__":
    main()
