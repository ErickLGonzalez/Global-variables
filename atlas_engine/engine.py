"""Atlas Engine v0.1 -- treating the restraint matrix ITSELF as a
constraint-satisfaction object ("solving the matrix" at the structural
level).

Idea: the columns are not independent. Established theorems connect
restraint types, so an H entry in one column can FORCE at least P in
another, per row type. Encoding those theorems as implication rules and
running fixpoint propagation turns the matrix into a derivation object:
machine-proposed upgrades with explicit theorem chains, human-ratified
via atlas edit records.

Discipline (hard rules of this engine):
  1. Rules only ever RAISE a cell to P(propagated). Promotion to H always
     requires a human edit record -- the engine cannot mint H.
  2. A rule whose conclusion targets a '-' (not-applicable) cell does not
     silently apply; it emits a TENSION for human review (either the '-'
     is wrong or the rule's row-scope is wrong -- both are findings).
  3. Every propagated cell carries its full derivation chain (rule name,
     anchor theorem, source cells).
  4. Propagation runs to a fixpoint; non-termination or a downgrade
     attempt is a hard error (the rule set is monotone by construction).

Levels: H=3, P=2, ?=1, -=0(NA). Propagated cells get level 2 with tag.
"""

from typing import Dict, List

H, P, Q, NA = 3, 2, 1, 0
LVL = {"H": H, "P": P, "?": Q, "-": NA}
NAME = {v: k for k, v in LVL.items()}

COLS = ["Sym", "Pos", "Uni", "Cau", "Cmp", "RG", "Top", "Thm"]

# Restraint Matrix v0.5, faithfully transcribed (levels only; annotations
# live in the atlas document). Row "type" drives rule applicability.
# Historical input for the first engine pass (pre-S1 ratification).
MATRIX_V05: Dict[str, Dict] = {
    "c":        {"type": "kinematic", "Sym": "H", "Pos": "-", "Uni": "-", "Cau": "H", "Cmp": "P", "RG": "-", "Top": "-", "Thm": "?"},
    "hbar":     {"type": "quantum",   "Sym": "P", "Pos": "H", "Uni": "H", "Cau": "P", "Cmp": "H", "RG": "-", "Top": "P", "Thm": "P"},
    "G":        {"type": "gravity",   "Sym": "H", "Pos": "P", "Uni": "-", "Cau": "H", "Cmp": "P", "RG": "?", "Top": "P", "Thm": "H"},
    "k_B":      {"type": "thermal",   "Sym": "P", "Pos": "H", "Uni": "-", "Cau": "-", "Cmp": "H", "RG": "-", "Top": "-", "Thm": "H"},
    "alpha":    {"type": "gauge_qft", "Sym": "H", "Pos": "P", "Uni": "H", "Cau": "H", "Cmp": "H", "RG": "H", "Top": "P", "Thm": "P"},
    "alpha_s":  {"type": "gauge_qft", "Sym": "H", "Pos": "P", "Uni": "H", "Cau": "H", "Cmp": "H", "RG": "H", "Top": "H", "Thm": "P"},
    "EW_block": {"type": "gauge_qft", "Sym": "H", "Pos": "P", "Uni": "H", "Cau": "H", "Cmp": "H", "RG": "H", "Top": "P", "Thm": "P"},
    "lambda_H": {"type": "gauge_qft", "Sym": "P", "Pos": "H", "Uni": "H", "Cau": "H", "Cmp": "?", "RG": "H", "Top": "-", "Thm": "P"},
    "Yukawa":   {"type": "gauge_qft", "Sym": "H", "Pos": "P", "Uni": "H", "Cau": "P", "Cmp": "?", "RG": "H", "Top": "?", "Thm": "P"},
    "neutrino": {"type": "gauge_qft", "Sym": "H", "Pos": "P", "Uni": "H", "Cau": "P", "Cmp": "?", "RG": "P", "Top": "?", "Thm": "P"},
    "theta_QCD":{"type": "gauge_qft", "Sym": "H", "Pos": "P", "Uni": "H", "Cau": "P", "Cmp": "?", "RG": "H", "Top": "H", "Thm": "P"},
    "Lambda":   {"type": "cosmo",     "Sym": "P", "Pos": "?", "Uni": "-", "Cau": "H", "Cmp": "?", "RG": "?", "Top": "?", "Thm": "H"},
    "initial":  {"type": "cosmo",     "Sym": "P", "Pos": "H", "Uni": "P", "Cau": "P", "Cmp": "?", "RG": "P", "Top": "-", "Thm": "P"},
}

# Restraint Matrix v0.6 (S1 ratification): engine propagations + human
# adjudications (G Uni —→P). propagate(MATRIX_V06) must be a fixpoint.
MATRIX_V06: Dict[str, Dict] = {
    "c":        {"type": "kinematic", "Sym": "H", "Pos": "-", "Uni": "-", "Cau": "H", "Cmp": "P", "RG": "-", "Top": "-", "Thm": "?"},
    "hbar":     {"type": "quantum",   "Sym": "P", "Pos": "H", "Uni": "H", "Cau": "P", "Cmp": "H", "RG": "-", "Top": "P", "Thm": "P"},
    "G":        {"type": "gravity",   "Sym": "H", "Pos": "P", "Uni": "P", "Cau": "H", "Cmp": "P", "RG": "?", "Top": "P", "Thm": "H"},
    "k_B":      {"type": "thermal",   "Sym": "P", "Pos": "H", "Uni": "-", "Cau": "-", "Cmp": "H", "RG": "-", "Top": "-", "Thm": "H"},
    "alpha":    {"type": "gauge_qft", "Sym": "H", "Pos": "P", "Uni": "H", "Cau": "H", "Cmp": "H", "RG": "H", "Top": "P", "Thm": "P"},
    "alpha_s":  {"type": "gauge_qft", "Sym": "H", "Pos": "P", "Uni": "H", "Cau": "H", "Cmp": "H", "RG": "H", "Top": "H", "Thm": "P"},
    "EW_block": {"type": "gauge_qft", "Sym": "H", "Pos": "P", "Uni": "H", "Cau": "H", "Cmp": "H", "RG": "H", "Top": "P", "Thm": "P"},
    "lambda_H": {"type": "gauge_qft", "Sym": "P", "Pos": "H", "Uni": "H", "Cau": "H", "Cmp": "P", "RG": "H", "Top": "-", "Thm": "P"},
    "Yukawa":   {"type": "gauge_qft", "Sym": "H", "Pos": "P", "Uni": "H", "Cau": "P", "Cmp": "P", "RG": "H", "Top": "P", "Thm": "P"},
    "neutrino": {"type": "gauge_qft", "Sym": "H", "Pos": "P", "Uni": "H", "Cau": "P", "Cmp": "P", "RG": "P", "Top": "P", "Thm": "P"},
    "theta_QCD":{"type": "gauge_qft", "Sym": "H", "Pos": "P", "Uni": "H", "Cau": "P", "Cmp": "P", "RG": "H", "Top": "H", "Thm": "P"},
    "Lambda":   {"type": "cosmo",     "Sym": "P", "Pos": "P", "Uni": "-", "Cau": "H", "Cmp": "?", "RG": "?", "Top": "?", "Thm": "H"},
    "initial":  {"type": "cosmo",     "Sym": "P", "Pos": "H", "Uni": "P", "Cau": "P", "Cmp": "?", "RG": "P", "Top": "-", "Thm": "P"},
}

# Implication rules. Each: name, row-type scope, preconditions
# [(col, min_level)], conclusion col, anchor. CONSERVATIVE SET: only
# entries backed by established theorems or this repo's own certified
# benchmarks; anything weaker stays out.
RULES: List[Dict] = [
    {"name": "R-GNS", "scope": {"quantum", "gauge_qft"},
     "pre": [("Uni", H)], "post": "Pos",
     "anchor": "GNS construction: any state on a *-algebra with unitary "
               "dynamics yields PSD Gram matrices (positivity is not "
               "optional for quantum-type rows)."},
    {"name": "R-CLUSTER", "scope": {"gauge_qft"},
     "pre": [("Uni", H), ("Cau", P)], "post": "Cmp",
     "anchor": "Cluster decomposition theorem (Weinberg QTF I; Haag): "
               "locality + Poincare covariance (encoded in the gauge_qft "
               "TYPE, not the internal-Sym cell) force composition "
               "restraints on all couplings. Internal certificate: B5 "
               "(edit-002); ratified edit-004. Sym-column convention "
               "(v0.6): dominant restraint in cell; spacetime locality "
               "via row TYPE (annotate, do not split)."},
    {"name": "R-DISPERSION", "scope": {"gauge_qft"},
     "pre": [("Cau", H), ("Uni", H)], "post": "Pos",
     "anchor": "Forward-limit dispersion relations: analyticity + "
               "unitarity imply positivity bounds on coefficients "
               "(Adams et al. 2006)."},
    {"name": "R-KMS", "scope": {"quantum", "gauge_qft", "gravity"},
     "pre": [("Uni", H), ("Pos", P)], "post": "Thm",
     "anchor": "KMS condition / Tomita-Takesaki: unitary dynamics with a "
               "positive state supports equilibrium (thermal) structure; "
               "thermodynamic restraints apply."},
    {"name": "R-ANOMALY", "scope": {"gauge_qft"},
     "pre": [("Sym", H), ("Uni", H)], "post": "Top",
     "anchor": "Anomaly cancellation: gauge symmetry + unitarity force "
               "topological (integrality) constraints on charge "
               "assignments (the 1970s solved blank)."},
    {"name": "R-GSL-CMP", "scope": {"gravity"},
     "pre": [("Thm", H), ("Cau", H)], "post": "Cmp",
     "anchor": "Hawking area theorem (NEC) + GSL: horizon thermodynamics "
               "with causal structure forces the composition law. "
               "Internal certificate: B4 REAL (edit-001)."},
    {"name": "R-SCHUR-QNEC", "scope": {"gravity"},
     "pre": [("Thm", H), ("Uni", P)], "post": "Pos",
     "anchor": "QNEC as Schur-pivot positivity (B6, edit-003; Wall 2011; "
               "BFKW 2017). On MATRIX_V05 (Uni='-') this rule emitted the "
               "NA tension that motivated edit-006 (G Uni —→P semiclassical). "
               "On MATRIX_V06 the precondition holds; Pos already P."},
    {"name": "R-DS-ENTROPY", "scope": {"cosmo"},
     "pre": [("Thm", H), ("Cau", H)], "post": "Pos",
     "anchor": "Finite horizon entropy (Gibbons-Hawking) bounds accessible "
               "state space => Gram positivity with effective rank bounds "
               "(conjecture ?7's weak direction: positivity applies, its "
               "rank form remains ?). Ratified edit-006."},
    # Standing growth (S1): theorem-anchored; currently dormant on the
    # filled matrix (Uni already H wherever Pos≥H in scope).
    {"name": "R-OS-UNI", "scope": {"quantum", "gauge_qft"},
     "pre": [("Pos", H)], "post": "Uni",
     "anchor": "Osterwalder-Schrader reconstruction: reflection positivity "
               "+ Euclidean axioms reconstruct unitary Lorentzian dynamics "
               "(OS positivity => Uni)."},
    # Standing growth (S2): relative-entropy positivity ties Thm → Pos.
    {"name": "R-REL-ENTROPY-POS", "scope": {"quantum", "gravity"},
     "pre": [("Thm", H)], "post": "Pos",
     "anchor": "Araki relative entropy S(rho||sigma)>=0 is operator-algebra "
               "positivity on state space; links thermodynamics/information "
               "to the Pos column. S2 free-fermion GNS probe "
               "(certificates/s2_gns_certificate.json) instantiates the "
               "vacuum Gram ray of the QNEC matrix M; full state-independent "
               "operator pair remains open."},
]


def propagate(matrix=None, rules=None):
    M = {r: dict(v) for r, v in (matrix or MATRIX_V05).items()}
    rules = rules or RULES
    lv = {r: {c: LVL[M[r][c]] for c in COLS} for r in M}
    derivations, tensions = [], []
    changed = True
    iterations = 0
    while changed:
        changed = False
        iterations += 1
        if iterations > 50:
            raise RuntimeError("non-monotone rule set: fixpoint not reached")
        for rule in rules:
            for row, data in M.items():
                if data["type"] not in rule["scope"]:
                    continue
                pre_na = [c for c, m in rule["pre"] if lv[row][c] == NA]
                pre_ok = all(lv[row][c] >= m for c, m in rule["pre"]
                             if lv[row][c] != NA)
                if pre_na and pre_ok:
                    key = (rule["name"], row, "pre")
                    if key not in {(t["rule"], t["row"], t.get("kind"))
                                   for t in tensions}:
                        tensions.append({"rule": rule["name"], "row": row,
                                         "kind": "pre",
                                         "target": rule["post"],
                                         "blocked_by_NA": pre_na,
                                         "finding": "rule blocked SOLELY by "
                                         "NA precondition cell(s): the NA "
                                         "status is under pressure -- human "
                                         "review",
                                         "anchor": rule["anchor"]})
                    continue
                if not all(lv[row][c] >= m for c, m in rule["pre"]):
                    continue
                tgt = rule["post"]
                if lv[row][tgt] == NA:
                    key = (rule["name"], row)
                    if key not in {(t["rule"], t["row"]) for t in tensions}:
                        tensions.append({"rule": rule["name"], "row": row,
                                         "target": tgt,
                                         "finding": "rule concludes on an NA "
                                         "cell: either the NA is wrong or the "
                                         "rule scope is wrong -- human review",
                                         "anchor": rule["anchor"]})
                    continue
                if lv[row][tgt] < P:
                    lv[row][tgt] = P
                    derivations.append({
                        "row": row, "cell": tgt,
                        "upgrade": f"? -> P(propagated)",
                        "rule": rule["name"],
                        "from_cells": [f"{c}>={NAME[m]}" for c, m in rule["pre"]],
                        "anchor": rule["anchor"]})
                    changed = True
    out_matrix = {r: {c: NAME[lv[r][c]] for c in COLS} for r in M}
    return {"iterations": iterations, "propagated": derivations,
            "tensions": tensions, "matrix_after": out_matrix,
            "note": "P(propagated) entries are machine-derived candidates; "
                    "each requires a human-ratified atlas edit record before "
                    "entering an atlas version. The engine cannot mint H."}
