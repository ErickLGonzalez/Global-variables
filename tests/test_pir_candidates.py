"""Candidate lattice + GVAR rules (P5a) and two-hash fingerprints (P5b).

C1  GVAR rules emit candidates + test obligations only; a rule fires on its
    required predicates and is blocked by a forbidden one.
C2  POSITIVE FIXTURE: two compatible families, no in-scope discriminator ->
    OBSERVATIONALLY_EQUIVALENT; L3 hypotheses retained in parallel.
C3  NEGATIVE FIXTURE: the discriminating intervention is declared ->
    NONIDENTIFIABLE; a single compatible family -> PERMITTED (identified);
    none -> REJECTED.
F1  Two-hash: the full (similarity-invariant) fingerprint is stable under a
    representation-only change; the specific fingerprint is not.
F2  B8 blind grammar ID as fingerprint lookup: a known grammar is IDENTIFIED;
    a full-hash collision with a different specific hash is filed as
    REPRESENTATION_DEPENDENT.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pir import candidates as C
from pir import fingerprints as FP

FAILURES = []


def check(label, errors):
    if errors:
        FAILURES.append((label, errors)); print(f"  [FAIL] {label}")
        for e in errors[:6]:
            print(f"         - {e}")
    else:
        print(f"  [ ok ] {label}")


RULES = [
    {"rule_id": "r_ham", "family": "hamiltonian",
     "requires_predicates": ["Sym", "Pos"],
     "test_obligation": {"intervention": "int_time_reversal",
                         "separates": ["gradient_flow"]}},
    {"rule_id": "r_grad", "family": "gradient_flow",
     "requires_predicates": ["Pos"], "forbids_predicates": ["Uni"],
     "test_obligation": {"intervention": "int_time_reversal",
                         "separates": ["hamiltonian"]}},
    {"rule_id": "r_cptp", "family": "quantum_cptp",
     "requires_predicates": ["Pos", "Cmp"]},
]


def c1_rules():
    preds = {"Sym", "Pos"}                      # ham fires; grad fires; cptp no (needs Cmp)
    cands = C.apply_rules(RULES, preds)
    fams = sorted(c.family for c in cands)
    errs = []
    if fams != ["gradient_flow", "hamiltonian"]:
        errs.append(f"unexpected candidate families {fams}")
    if not all(c.test_obligation for c in cands):
        errs.append("candidates missing test obligations")
    # forbid: add Uni -> gradient_flow blocked.
    cands2 = C.apply_rules(RULES, {"Sym", "Pos", "Uni"})
    if any(c.family == "gradient_flow" for c in cands2):
        errs.append("forbids_predicates did not block gradient_flow")
    check("C1 GVAR rules emit candidates + obligations; forbid predicate blocks", errs)


def c2_positive_oe():
    cands = C.apply_rules(RULES, {"Sym", "Pos"})
    res = C.evaluate(cands, declared_interventions=[])
    hyps = C.to_hypotheses(cands, "eqc_demo")
    fact = C.lattice_fact(res, "eqc_demo")
    errs = []
    if res.verdict != "OBSERVATIONALLY_EQUIVALENT":
        errs.append(f"expected OE, got {res.verdict}")
    if fact.verdict.value != "OBSERVATIONALLY_EQUIVALENT":
        errs.append("lattice fact verdict mismatch")
    if len(hyps) != 2 or {h.status.value for h in hyps} != {"OBSERVATIONALLY_EQUIVALENT_MEMBER"}:
        errs.append("hypotheses not retained in parallel as OE members")
    check("C2 positive fixture -> OBSERVATIONALLY_EQUIVALENT, hypotheses retained", errs)


def c3_negative():
    cands = C.apply_rules(RULES, {"Sym", "Pos"})
    # declared discriminator -> NONIDENTIFIABLE
    res = C.evaluate(cands, declared_interventions=["int_time_reversal"])
    errs = []
    if res.verdict != "NONIDENTIFIABLE":
        errs.append(f"expected NONIDENTIFIABLE, got {res.verdict}")
    # single compatible family -> PERMITTED (identified). {Pos,Cmp,Uni}: cptp
    # fires; gradient_flow is blocked by its forbidden Uni; hamiltonian needs Sym.
    one = C.apply_rules(RULES, {"Pos", "Cmp", "Uni"})    # only quantum_cptp
    r1 = C.evaluate(one, [])
    if r1.verdict != "PERMITTED" or r1.detail.get("identified_family") != "quantum_cptp":
        errs.append(f"single-family case not PERMITTED/identified: {r1.verdict}")
    # none compatible -> REJECTED
    r0 = C.evaluate(C.apply_rules(RULES, {"Top"}), [])
    if r0.verdict != "REJECTED":
        errs.append(f"empty candidate set not REJECTED: {r0.verdict}")
    check("C3 negative fixtures -> NONIDENTIFIABLE / PERMITTED / REJECTED", errs)


def f1_two_hash():
    base = {"psd_signature": {"rank": 3, "n_pos": 3}, "rank_sequence": [1, 2, 3],
            "symmetry_group": "SU(2)", "representation_label": "chart_A",
            "basis_order": [0, 1, 2]}
    # representation-only change: invariants identical, labels differ.
    rep = dict(base, representation_label="chart_B", basis_order=[2, 1, 0])
    errs = []
    if FP.full_fingerprint(base) != FP.full_fingerprint(rep):
        errs.append("full fingerprint changed under a representation-only edit")
    if FP.specific_fingerprint(base) == FP.specific_fingerprint(rep):
        errs.append("specific fingerprint failed to distinguish representations")
    # a genuine invariant change flips the full hash.
    diff = dict(base, rank_sequence=[1, 2, 4])
    if FP.full_fingerprint(diff) == FP.full_fingerprint(base):
        errs.append("full fingerprint blind to an invariant change")
    check("F1 full hash similarity-invariant; specific hash discriminates", errs)


def f2_b8_lookup():
    db = FP.KnownGrammarDB()
    g_ham = {"psd_signature": {"rank": 2}, "rank_sequence": [1, 2],
             "symmetry_group": "SO(3)", "representation_label": "A"}
    db.register("hamiltonian_v1", g_ham)
    db.register("cptp_v1", {"psd_signature": {"rank": 4}, "rank_sequence": [1, 2, 3, 4],
                            "symmetry_group": "U(1)"})
    errs = []
    # blind ID of the same grammar -> IDENTIFIED.
    r = db.identify(g_ham)
    if r["status"] != "IDENTIFIED" or r["grammar_id"] != "hamiltonian_v1":
        errs.append(f"blind ID failed: {r}")
    # collision: same invariants, different representation -> REPRESENTATION_DEPENDENT.
    g_collide = dict(g_ham, representation_label="B")   # same invariants, diff specific
    db.register("hamiltonian_alt", g_ham)               # same full+specific as v1
    r2 = db.identify(g_collide)
    if r2["status"] != "REPRESENTATION_DEPENDENT":
        errs.append(f"collision not flagged REPRESENTATION_DEPENDENT: {r2}")
    check("F2 B8 blind ID via fingerprint; collision -> REPRESENTATION_DEPENDENT", errs)


if __name__ == "__main__":
    print("== candidate lattice + fingerprints ==")
    c1_rules(); c2_positive_oe(); c3_negative(); f1_two_hash(); f2_b8_lookup()
    print("\n== SUMMARY ==")
    if FAILURES:
        print(f"FAIL: {len(FAILURES)} check(s) failed."); sys.exit(1)
    print("PASS: candidate lattice + GVAR rules + two-hash fingerprints live.")
    sys.exit(0)
