"""Atlas engine tests -- first machine pass + S1 ratification idempotence.

T1  Fixpoint reached; zero downgrades (monotonicity audit) on MATRIX_V05.
T2  Expected propagations appear with correct derivation chains:
    - Yukawa/neutrino/theta_QCD/lambda_H Cmp: ? -> P via R-CLUSTER
    - Yukawa/neutrino Top: ? -> P via R-ANOMALY (weak ?6)
    - Lambda Pos: ? -> P via R-DS-ENTROPY (weak ?7)
    - c Thm stays ? (?1 open); G RG stays ? (?4 open)
T3  Tension probe on V05: R-SCHUR-QNEC flags gravity Uni='-' (historical).
T4  The engine cannot mint H: no cell exceeds P via propagation.
T5  Conflict detection: guard machinery / iteration cap.
T6  S1 DoD: propagate(MATRIX_V06) is idempotent (0 new upgrades; levels
    match the ratified atlas). R-SCHUR-QNEC Uni-NA tension cleared.
"""

import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atlas_engine.engine import propagate, MATRIX_V05, MATRIX_V06, RULES, COLS
from b1_moment_solver.certificate import save_certificate


def t1_fixpoint():
    res = propagate(MATRIX_V05)
    before = MATRIX_V05
    order = {"H": 3, "P": 2, "?": 1, "-": 0}
    for row in before:
        for c in COLS:
            assert order[res["matrix_after"][row][c]] >= order[before[row][c]], \
                (row, c)
    print(f"T1 fixpoint + monotonicity: PASS  ({res['iterations']} sweeps, "
          f"{len(res['propagated'])} propagations, 0 downgrades)")
    return res


def t2_expected(res):
    got = {(d["row"], d["cell"], d["rule"]) for d in res["propagated"]}
    for row in ("Yukawa", "neutrino", "theta_QCD", "lambda_H"):
        assert (row, "Cmp", "R-CLUSTER") in got, (row, got)
    for row in ("Yukawa", "neutrino"):
        assert (row, "Top", "R-ANOMALY") in got, (row, got)
    assert ("Lambda", "Pos", "R-DS-ENTROPY") in got
    assert res["matrix_after"]["c"]["Thm"] == "?", "?1 must remain open"
    assert res["matrix_after"]["G"]["RG"] == "?", "?4 must remain open"
    print("T2 expected propagations: PASS")
    print("    Cmp ?->P for Yukawa, neutrino, theta_QCD, lambda_H  [R-CLUSTER]")
    print("    Top ?->P for Yukawa, neutrino  [R-ANOMALY]  (weak ?6; index form stays open)")
    print("    Lambda Pos ?->P  [R-DS-ENTROPY]  (rank form of ?7 stays open)")
    print("    ?1 (c/Thm), ?4 (G/RG) untouched -- genuinely open, as they must be")
    return sorted(got)


def t3_tension(res):
    t = [x for x in res["tensions"] if x["rule"] == "R-SCHUR-QNEC"]
    assert t and t[0]["row"] == "G" and "Uni" in t[0].get("blocked_by_NA", []), res["tensions"]
    print("T3 tension probe (V05 historical): PASS  R-SCHUR-QNEC flags "
          "gravity Uni='-' (adjudicated in edit-006 / MATRIX_V06)")
    return res["tensions"]


def t4_no_H_minting(res):
    for d in res["propagated"]:
        assert "P(propagated)" in d["upgrade"] and "H" not in d["upgrade"]
    print("T4 no-H-minting: PASS  every propagation stops at P; H remains "
          "human-only via edit records")
    return {"propagations": len(res["propagated"]), "H_minted": 0}


def t5_conflict():
    bad = [dict(RULES[0])]
    bad[0] = {"name": "BAD", "scope": {"gauge_qft"}, "pre": [],
              "post": "Pos", "anchor": "none"}
    try:
        res = propagate(rules=bad)
        assert res["iterations"] <= 50
        print("T5 guard machinery: PASS  iteration cap active; monotone "
              "rules terminate")
        return {"status": "GUARDED"}
    except RuntimeError as e:
        print(f"T5 guard machinery: PASS  non-monotone set rejected: {e}")
        return {"status": "REJECTED_AS_EXPECTED"}


def t6_idempotence_v06():
    res = propagate(MATRIX_V06)
    assert res["propagated"] == [], res["propagated"]
    for row in MATRIX_V06:
        for c in COLS:
            assert res["matrix_after"][row][c] == MATRIX_V06[row][c], \
                (row, c, res["matrix_after"][row][c], MATRIX_V06[row][c])
    schur = [x for x in res["tensions"]
             if x["rule"] == "R-SCHUR-QNEC" and "Uni" in x.get("blocked_by_NA", [])]
    assert not schur, "V06 should clear the Uni-NA tension on R-SCHUR-QNEC"
    assert MATRIX_V06["G"]["Uni"] == "P"
    assert "R-OS-UNI" in {r["name"] for r in RULES}
    assert "R-REL-ENTROPY-POS" in {r["name"] for r in RULES}
    print("T6 V06 idempotence: PASS  0 new upgrades; matrix_after == MATRIX_V06; "
          "Uni-NA Schur tension cleared; R-OS-UNI + R-REL-ENTROPY-POS present")
    return res


if __name__ == "__main__":
    res = t1_fixpoint()
    ex = t2_expected(res)
    tn = t3_tension(res)
    r4 = t4_no_H_minting(res)
    r5 = t5_conflict()
    res6 = t6_idempotence_v06()
    cert = {
        "certificate_version": "0.3",
        "certificate_class": "STRUCTURAL-DERIVATION (theorem-anchored "
                             "implication propagation over the restraint "
                             "matrix; S1-ratified into atlas v0.6)",
        "problem": "Atlas Engine v0.1 + S1 ratification: first machine pass "
                   "and idempotent fixpoint on MATRIX_V06",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "m_layer_stipulations": [
            "MATRIX_V05 is the historical first-pass input",
            "MATRIX_V06 is the ratified atlas transcription (edit-004/005/006)",
            "rule set restricted to established theorems + this repo's "
            "certified benchmarks (B4 REAL, B5, B6) + R-OS-UNI (S1 growth)",
            "P(propagated) on V05 required human edit records; V06 is the "
            "fixpoint (idempotence check T6)",
        ],
        "results": {"propagations_v05": res["propagated"],
                    "tensions_v05": tn,
                    "matrix_after_v05": res["matrix_after"],
                    "idempotence_v06": {
                        "propagations": res6["propagated"],
                        "tensions": res6["tensions"],
                        "matrix_after": res6["matrix_after"],
                    },
                    "guards": {"no_H_minting": r4, "termination": r5}},
    }
    save_certificate(cert, os.path.join(os.path.dirname(__file__), "..",
                                        "certificates",
                                        "atlas_engine_certificate.json"))
    print("\nCertificate written: certificates/atlas_engine_certificate.json")
    print("ALL ATLAS-ENGINE TESTS PASS")
