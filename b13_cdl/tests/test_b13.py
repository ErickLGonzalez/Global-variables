"""B13-CDL headless test harness (blueprint-B1 pattern).

Runs: schema validation of ledger + falsifiers, all eight pipelines, certificate
schema validation, content-hash identity (Tier 1), and the PIR-fact bridge with
assumption-taint invalidation (Tier 3). Exit nonzero on any failure.

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
    emitted = {}
    for name, fn in pipelines:
        try:
            cert = fn()
            errs = common.validate(cert, cert_schema, f"$({name})")
            check(f"pipeline {name} -> {cert['verdict'][:64]}", errs)
            if not errs:
                emitted[name] = cert
                path = common.write_certificate(cert)
                print(f"         cert: {os.path.relpath(path, common.PKG_ROOT)}")
        except Exception as exc:  # noqa: BLE001 — harness must report, not crash
            check(f"pipeline {name}", [f"exception: {exc!r}"])

    # 3b. Tier-1 identity: certificate_id is a reproducible content hash, and the
    #     filename is stable per pipeline (rerun overwrites, no UUID churn).
    id_errs = []
    for name, cert in emitted.items():
        expected = f"b13cdl-{name}-{common._content_hash(cert)}"
        if cert["certificate_id"] != expected:
            id_errs.append(f"{name}: id {cert['certificate_id']} != content hash {expected}")
        if common.certificate_filename(cert) != f"b13cdl-{name}.json":
            id_errs.append(f"{name}: unstable filename {common.certificate_filename(cert)}")
    check("certificate ids are content hashes + stable filenames (Tier 1)", id_errs)

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

    # 5. Tier-3: emit PIR facts and exercise assumption-taint / invalidation.
    from src.cdl import pir_bridge
    if not pir_bridge.available():
        check("PIR bridge (Tier 3)", ["pir package not importable from repo root"])
    else:
        import pir as pirpkg
        from pir import FactStore
        certs = list(emitted.values())
        # (a) Every certificate maps to a valid PIR fact (constructor enforces
        #     the honesty invariants: HEURISTIC E3 needs a warning, SOUND cannot
        #     be E3/E4, DOMAIN/MEASUREMENT facts need a measurement interface).
        try:
            store, facts = pir_bridge.build_store(certs)
            build_err = []
        except Exception as exc:  # noqa: BLE001
            store, facts, build_err = None, [], [f"fact build failed: {exc!r}"]
        check(f"PIR facts built for all {len(certs)} pipelines (Tier 3)", build_err)

        if store is not None:
            # (b) Each fact validates against pir/schema/fact.schema.json.
            fact_schema = common.load_json(
                os.path.dirname(pirpkg.__file__), "schema", "fact.schema.json")
            serr = []
            for f in facts:
                serr.extend(pirpkg.jsonschema_mini.iter_errors(fact_schema, f.to_dict()))
            check("PIR facts validate against fact.schema.json", serr)

            # (c) CONDITIONAL(X) is assumption-taint: invalidating asm:GRH
            #     downgrades exactly the GRH-conditional Miller fact, and leaves
            #     the unconditional physics facts (e.g. varying_constants) intact.
            gm_fact = next(f for f in facts if f.analyzer.id == "b13cdl.grh_miller")
            assert "asm:GRH" in gm_fact.assumptions, gm_fact.assumptions
            affected = store.invalidate_assumption("asm:GRH", reason="GRH withdrawn (drill)")
            vc_fact = next(f for f in facts if f.analyzer.id == "b13cdl.varying_constants")
            errs = []
            if gm_fact.fact_id not in affected:
                errs.append("asm:GRH invalidation did not reach grh_miller fact")
            if store.get(gm_fact.fact_id).status.value != "DOWNGRADED":
                errs.append("grh_miller fact not DOWNGRADED after invalidation")
            if store.get(vc_fact.fact_id).status.value != "SUPPORTED":
                errs.append("varying_constants fact wrongly affected by asm:GRH")
            check("invalidating asm:GRH downgrades only GRH-conditional facts", errs)

            # (d) Write the stable PIR-fact view artifact (rebuild clean store).
            doc = pir_bridge.facts_document(certs)
            out = os.path.join(common.CERT_DIR, "pir_facts.json")
            with open(out, "w") as fh:
                json.dump(doc, fh, indent=2, sort_keys=True)
            print(f"         pir view: {os.path.relpath(out, common.PKG_ROOT)} "
                  f"({len(doc['facts'])} facts)")

    print("\n== SUMMARY ==")
    if FAILURES:
        print(f"FAIL: {len(FAILURES)} check(s) failed.")
        sys.exit(1)
    print("PASS: all checks green. Certificates in certificates/.")
    sys.exit(0)


if __name__ == "__main__":
    main()
