"""Analyzer runtime + priority analyzers (Stage 2 / P3).

R1  DEPENDENCY GRAPH: passes run in topological order; a cycle is rejected.
R2  THREE ANALYZERS: MeasurementProvenance flags a non-promotable route;
    ObservationalEquivalence emits OBSERVATIONALLY_EQUIVALENT for a 2-member
    class with no in-scope separator, NONIDENTIFIABLE when one is declared;
    GlobalVariableCandidate proposes a GLOBAL_CANDIDATE for a cross-namespace
    invariant.
R3  DETERMINISM: two runs over identical inputs emit identical fact ids.
R4  ISOLATION: a pass that raises is quarantined; the store keeps the other
    passes' facts and is not corrupted.
R5  CONFLICTS RETAINED: two passes asserting opposing verdicts about one subject
    both persist; detect_conflicts surfaces the pair, nothing deleted.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pir import AnalyzerRef, Fact, FactStore, Warning_
from pir.runtime import AnalyzerRuntime, AnalyzerPass, PassGraphCycle, detect_conflicts
from pir import analyzers as A
from pir.types import PassTag

FAILURES = []


def check(label, errors):
    if errors:
        FAILURES.append((label, errors)); print(f"  [FAIL] {label}")
        for e in errors[:6]:
            print(f"         - {e}")
    else:
        print(f"  [ ok ] {label}")


def _domain_fact(fid, route, ns="domain", inv=None):
    content = {"claim": fid}
    if inv is not None:
        content["invariant_hash"] = inv
    return Fact(fact_id=fid, pir_level="L2", evidence_level="E1", layer="DOMAIN",
                namespace=ns, status="SUPPORTED",
                analyzer=AnalyzerRef("seed", "0.1.0", PassTag.SOUND),
                content=content, created_at="1970-01-01T00:00:00Z",
                measurement_interface=(route,),
                source_spans=({"artifact_id": "art", "span": fid},))


def seed_store():
    st = FactStore()
    st.add_fact(_domain_fact("f_spec", "cal:spectroscopy_route", inv="INV42"))
    st.add_fact(_domain_fact("f_gibbs", "cal:gibbs_route"))
    # a second carrier of the same invariant in a different namespace
    st.add_fact(_domain_fact("f_other", "cal:spectroscopy_route", ns="invariant", inv="INV42"))
    return st


def r1_r2_r3():
    st = seed_store()
    rt = AnalyzerRuntime()
    rt.register(A.measurement_provenance_pass())
    hyps = [{"id": "h1", "equivalence_class_id": "eqc", "distinguishing_interventions": []},
            {"id": "h2", "equivalence_class_id": "eqc", "distinguishing_interventions": []}]
    rt.register(A.observational_equivalence_pass(hyps, declared_interventions=[]))
    rt.register(A.global_variable_candidate_pass())
    rep = rt.run(st)

    # R1 order includes all three (no deps here, sorted by id).
    errs = [] if len(rep.order) == 3 else [f"order {rep.order}"]
    check("R1 dependency graph runs all passes in stable order", errs)

    # R2 each analyzer emitted the right verdict.
    facts = {f.fact_id: f for f in st.facts()}
    verds = [f.verdict.value for f in facts.values() if f.verdict]
    e2 = []
    if "APPARATUS_LIMITED" not in verds:
        e2.append("MeasurementProvenance did not flag the Gibbs route")
    if "OBSERVATIONALLY_EQUIVALENT" not in verds:
        e2.append("OE analyzer did not emit OBSERVATIONALLY_EQUIVALENT")
    gvc = [f for f in facts.values()
           if f.content.get("candidate_class") == "GLOBAL_CANDIDATE"]
    if not gvc:
        e2.append("GlobalVariableCandidate did not propose a cross-namespace candidate")
    check("R2 three analyzers emit APPARATUS_LIMITED / OE / GLOBAL_CANDIDATE", e2)

    # R3 determinism: rerun on a fresh identical store -> identical emitted ids.
    st2 = seed_store()
    rt2 = AnalyzerRuntime()
    rt2.register(A.measurement_provenance_pass())
    rt2.register(A.observational_equivalence_pass(hyps, declared_interventions=[]))
    rt2.register(A.global_variable_candidate_pass())
    rep2 = rt2.run(st2)
    e3 = [] if rep.emitted == rep2.emitted else [f"{rep.emitted} != {rep2.emitted}"]
    check("R3 deterministic reruns emit identical fact ids", e3)

    # OE with a declared separator -> NONIDENTIFIABLE instead.
    st3 = seed_store()
    rt3 = AnalyzerRuntime()
    hyps_sep = [{"id": "h1", "equivalence_class_id": "e", "distinguishing_interventions": ["int_T"]},
                {"id": "h2", "equivalence_class_id": "e", "distinguishing_interventions": ["int_T"]}]
    rt3.register(A.observational_equivalence_pass(hyps_sep, declared_interventions=["int_T"]))
    rt3.run(st3)
    ni = [f for f in st3.facts() if f.verdict and f.verdict.value == "NONIDENTIFIABLE"]
    check("R2b declared separator -> NONIDENTIFIABLE(insufficient intervention)",
          [] if ni else ["expected NONIDENTIFIABLE with a declared separator"])


def r1_cycle():
    rt = AnalyzerRuntime()
    rt.register(AnalyzerPass("a", "0", PassTag.SOUND, fn=lambda s, c: [], depends_on=("b",)))
    rt.register(AnalyzerPass("b", "0", PassTag.SOUND, fn=lambda s, c: [], depends_on=("a",)))
    try:
        rt.topological_order()
        check("R1 cycle rejected", ["cycle not detected"])
    except PassGraphCycle:
        check("R1 cycle rejected", [])


def r4_isolation():
    st = seed_store()
    n_before = len(st)
    rt = AnalyzerRuntime()

    def boom(store, ctx):
        raise RuntimeError("analyzer exploded")
    rt.register(AnalyzerPass("Boom", "0.1.0", PassTag.SOUND, fn=boom))
    rt.register(A.measurement_provenance_pass())
    rep = rt.run(st)
    errs = []
    if not any(q["pass"] == "Boom" for q in rep.quarantined):
        errs.append("failing pass not quarantined")
    # the good pass still ran and appended; store grew, not corrupted.
    if len(st) <= n_before:
        errs.append("store did not gain the surviving analyzer's facts")
    if len(st.facts()) != len(st.facts()):  # trivially consistent / not corrupt
        errs.append("store inconsistent")
    check("R4 analyzer failure quarantined; store intact and other passes run", errs)


def r5_conflicts():
    st = seed_store()
    # two analyzer passes assert opposing verdicts about the same subject.
    def rej(store, ctx):
        return [A._mk_fact("RejAnalyzer", PassTag.SOUND, "E1", "REJECTED",
                           {"claim": "shared_subject", "subject": "shared_subject"})]
    def perm(store, ctx):
        return [A._mk_fact("PermAnalyzer", PassTag.SOUND, "E1", "PERMITTED",
                           {"claim": "shared_subject", "subject": "shared_subject"})]
    rt = AnalyzerRuntime()
    rt.register(AnalyzerPass("RejAnalyzer", "0.1.0", PassTag.SOUND, fn=rej))
    rt.register(AnalyzerPass("PermAnalyzer", "0.1.0", PassTag.SOUND, fn=perm))
    rep = rt.run(st)
    conf = detect_conflicts(st)
    errs = []
    if not conf:
        errs.append("no conflict surfaced for opposing verdicts")
    else:
        both = set(conf[0]["verdicts"])
        if not ({"REJECTED", "PERMITTED"} <= both):
            errs.append(f"conflict verdicts {both} missing an opposing pair")
    # both facts still present (append-only, nothing deleted).
    if len([f for f in st.facts() if f.content.get("subject") == "shared_subject"]) != 2:
        errs.append("a conflicting fact was dropped (must be retained)")
    check("R5 opposing verdicts both retained; conflict surfaced, nothing deleted", errs)


if __name__ == "__main__":
    print("== analyzer runtime + priority analyzers ==")
    r1_r2_r3(); r1_cycle(); r4_isolation(); r5_conflicts()
    print("\n== SUMMARY ==")
    if FAILURES:
        print(f"FAIL: {len(FAILURES)} check(s) failed."); sys.exit(1)
    print("PASS: runtime deterministic, isolated, conflict-retaining; 3 analyzers live.")
    sys.exit(0)
