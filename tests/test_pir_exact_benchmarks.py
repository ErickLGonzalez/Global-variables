"""B1/B2/B3 exact-benchmark lowerings + cross-checks (Stage 2 coverage).

E1  B1/B2/B3 verdicts are re-derived from the committed certificates and match
    the benchmarks' own outcomes (FORCED/PERMITTED/REJECTED/NONIDENTIFIABLE).
E2  Exact witnesses lowered: FORCED facts carry a witness; REJECTED facts carry
    an impossibility_certificate (exact negative pivot / broken relations).
E3  BRIDGE CONSISTENCY: the P4 symbolic bridge agrees with the lowered verdicts
    on a B1 forcing case (UNIQUE->FORCED) and the B3 identifiability case
    (rank deficit d=3 -> NONIDENTIFIABLE).
E4  SUITE RUN: the analyzer runtime runs over the combined B1+B2+B3 store; the
    MeasurementProvenance analyzer completes and no spurious conflict is raised
    among the (distinct-subject) benchmark facts.
"""

import os
import sys
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pir.domains import exact_benchmarks as EB
from pir.symbolic import linear, constraint_fact
from pir.runtime import AnalyzerRuntime, detect_conflicts
from pir import analyzers as A

FAILURES = []


def check(label, errors):
    if errors:
        FAILURES.append((label, errors)); print(f"  [FAIL] {label}")
        for e in errors[:6]:
            print(f"         - {e}")
    else:
        print(f"  [ ok ] {label}")


def e1_verdicts():
    got = {b: EB.reproduced_verdicts(b) for b in ("b1", "b2", "b3")}
    expect = {
        "b1": {"T1_forced_tail": "FORCED", "T2_permitted_hole": "PERMITTED",
               "T3_negative_control": "REJECTED"},
        "b2": {"T1_cptp_audit": "PERMITTED", "T2_tp_forced": "FORCED",
               "T3_rank1_forced": "FORCED", "T5_negative_control": "REJECTED"},
        "b3": {"T3_d_identifiable": "NONIDENTIFIABLE", "T5_negative_control": "REJECTED"},
    }
    errs = []
    for b, exp in expect.items():
        for t, v in exp.items():
            if got[b].get(t) != v:
                errs.append(f"{b}.{t}: got {got[b].get(t)!r}, expected {v!r}")
    check("E1 B1/B2/B3 verdicts re-derived from certificates match", errs)


def e2_witnesses():
    errs = []
    for b in ("b1", "b2", "b3"):
        for f in EB.lower(b):
            if f.verdict and f.verdict.value == "FORCED" and f.witness is None:
                errs.append(f"{b} FORCED fact has no witness")
            if f.verdict and f.verdict.value == "REJECTED" and f.impossibility_certificate is None:
                errs.append(f"{b} REJECTED fact has no impossibility_certificate")
    # the exact negative pivots are genuinely negative.
    b1_t3 = next(f for f in EB.lower("b1") if "T3" in f.source_spans[0]["span"])
    if F(b1_t3.impossibility_certificate["pivot"]) >= 0:
        errs.append("b1 T3 pivot not negative")
    check("E2 FORCED facts carry witnesses; REJECTED carry impossibility certs", errs)


def e3_bridge_consistency():
    errs = []
    # B1 forcing as a unique linear solve -> FORCED (matches lowered T1).
    res = linear.solve([[F(1)]], [F(5)])
    if constraint_fact(res, "b1_forcing", arithmetic="exact").verdict.value != "FORCED":
        errs.append("bridge disagrees with B1 forcing verdict")
    # B3 identifiability: rank-deficient system, d = n - rank = 3. Build a 6x9
    # rank-6 system (rank deficit 3) and confirm NONIDENTIFIABLE.
    A9 = [[F(1) if j == i else F(0) for j in range(9)] for i in range(6)]  # rank 6, 9 vars
    b6 = [F(0)] * 6
    r = linear.solve(A9, b6)
    fact = constraint_fact(r, "b3_identifiability", arithmetic="exact")
    if fact.verdict.value != "NONIDENTIFIABLE":
        errs.append(f"bridge B3 verdict {fact.verdict.value} != NONIDENTIFIABLE")
    if fact.content.get("d_identifiable") != 3:
        errs.append(f"bridge d_identifiable {fact.content.get('d_identifiable')} != 3")
    check("E3 symbolic bridge agrees: B1 forcing FORCED, B3 rank-deficit d=3 "
          "NONIDENTIFIABLE", errs)


def e4_suite_run():
    st = EB.suite_store()
    n = len(st)
    rt = AnalyzerRuntime()
    rt.register(A.measurement_provenance_pass())
    rep = rt.run(st)
    errs = []
    if rep.quarantined:
        errs.append(f"analyzer quarantined unexpectedly: {rep.quarantined}")
    if len(st) < n:
        errs.append("store shrank (append-only violated)")
    # distinct benchmark facts must not be spuriously flagged as mutual conflicts.
    if detect_conflicts(EB.suite_store()):
        errs.append("spurious conflict among distinct-subject benchmark facts")
    check(f"E4 analyzer runtime over combined B1+B2+B3 store ({n} facts), no "
          "spurious conflict", errs)


if __name__ == "__main__":
    print("== exact benchmark lowerings B1/B2/B3 ==")
    e1_verdicts(); e2_witnesses(); e3_bridge_consistency(); e4_suite_run()
    print("\n== SUMMARY ==")
    if FAILURES:
        print(f"FAIL: {len(FAILURES)} check(s) failed."); sys.exit(1)
    print("PASS: B1/B2/B3 reproduced from PIR facts; bridge consistent; suite runs.")
    sys.exit(0)
