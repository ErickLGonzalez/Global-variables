"""Symbolic constraint bridge (Stage 2 / P4).

S1  B1 FORCING (exact): a flat-extension recurrence determines the unknown tail
    moment uniquely -> UNIQUE -> FORCED, with the exact value as SAT witness.
S2  B3 IDENTIFIABILITY (exact): a rank-deficient constraint Jacobian has a free
    direction -> UNDERDETERMINED -> NONIDENTIFIABLE, null vector as witness,
    d_identifiable = n - rank.
S3  INFEASIBLE: an inconsistent system -> INCONSISTENT -> REJECTED with a Farkas
    certificate (yᵀA = 0, yᵀb ≠ 0), independently verified.
S4  QUARANTINE: the same UNIQUE result under numeric arithmetic is capped to E3 /
    HEURISTIC with a located warning; exact stays E0 / SOUND.
"""

import os
import sys
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pir.symbolic import linear, constraint_fact

FAILURES = []


def check(label, errors):
    if errors:
        FAILURES.append((label, errors)); print(f"  [FAIL] {label}")
        for e in errors[:6]:
            print(f"         - {e}")
    else:
        print(f"  [ ok ] {label}")


def s1_b1_forcing():
    # Flat Hankel forcing: unknown m4 satisfies the rank-2 recurrence
    # m4 = 2*m3 - m2 (a concrete flat extension). One equation, one unknown x=m4.
    # Encoded A x = b with x=[m4]:  1*m4 = 2*m3 - m2  with m2=1, m3=3 -> m4=5.
    A = [[F(1)]]
    b = [F(2) * 3 - 1]           # = 5
    res = linear.solve(A, b)
    fact = constraint_fact(res, subject="B1:flat_extension_tail", arithmetic="exact")
    errs = []
    if res["status"] != "UNIQUE" or fact.verdict.value != "FORCED":
        errs.append(f"expected UNIQUE/FORCED, got {res['status']}/{fact.verdict}")
    if fact.witness["solution"] != ["5/1"]:
        errs.append(f"forced witness {fact.witness['solution']} != 5")
    if not linear.verify_solution(A, b, [F(5)]):
        errs.append("witness fails re-check")
    check("S1 B1 forcing -> FORCED with exact SAT witness (m4 = 5)", errs)


def s2_b3_identifiability():
    # Rank-deficient constraint Jacobian: 2 constraints, 3 unknowns, rank 2 ->
    # one free direction (a gauge/unidentified combination).
    A = [[F(1), F(1), F(0)],
         [F(0), F(1), F(1)]]
    b = [F(2), F(3)]
    res = linear.solve(A, b)
    fact = constraint_fact(res, subject="B3:constraint_jacobian", arithmetic="exact")
    errs = []
    if res["status"] != "UNDERDETERMINED" or fact.verdict.value != "NONIDENTIFIABLE":
        errs.append(f"expected UNDERDETERMINED/NONIDENTIFIABLE, got {res['status']}")
    if fact.content.get("d_identifiable") != 1:
        errs.append(f"d_identifiable {fact.content.get('d_identifiable')} != 1")
    nv = res["null_space"][0]
    if not linear.verify_null(A, nv):
        errs.append("null-space witness fails re-check (A v != 0)")
    check("S2 B3 identifiability -> NONIDENTIFIABLE, d_identifiable=1, null witness", errs)


def s3_infeasible_farkas():
    # x + y = 1 and x + y = 2: inconsistent. Farkas y=[1,-1]: yᵀA=0, yᵀb=-1.
    A = [[F(1), F(1)], [F(1), F(1)]]
    b = [F(1), F(2)]
    res = linear.solve(A, b)
    fact = constraint_fact(res, subject="infeasible_demo", arithmetic="exact")
    errs = []
    if res["status"] != "INCONSISTENT" or fact.verdict.value != "REJECTED":
        errs.append(f"expected INCONSISTENT/REJECTED, got {res['status']}")
    y = res["farkas"]
    if not linear.verify_farkas(A, b, y):
        errs.append(f"Farkas certificate {y} fails re-check")
    if fact.impossibility_certificate is None:
        errs.append("REJECTED fact carries no impossibility_certificate")
    check("S3 infeasible -> REJECTED with verified Farkas UNSAT certificate", errs)


def s4_quarantine():
    A = [[F(1)]]; b = [F(5)]
    res = linear.solve(A, b)
    exact = constraint_fact(res, subject="q", arithmetic="exact")
    numeric = constraint_fact(res, subject="q", arithmetic="float64")
    errs = []
    if not (exact.evidence_level.value == "E0" and exact.analyzer.tag.value == "SOUND"):
        errs.append("exact result should be E0/SOUND")
    if not (numeric.evidence_level.value == "E3" and numeric.analyzer.tag.value == "HEURISTIC"):
        errs.append("numeric result should be quarantined to E3/HEURISTIC")
    if not numeric.warnings:
        errs.append("quarantined numeric fact must carry a located warning")
    check("S4 solver output quarantined by evidence class (exact E0 vs numeric E3)", errs)


if __name__ == "__main__":
    print("== symbolic constraint bridge ==")
    s1_b1_forcing(); s2_b3_identifiability(); s3_infeasible_farkas(); s4_quarantine()
    print("\n== SUMMARY ==")
    if FAILURES:
        print(f"FAIL: {len(FAILURES)} check(s) failed."); sys.exit(1)
    print("PASS: exact SAT/UNSAT certificates lowered to PIR; quarantine enforced.")
    sys.exit(0)
