"""Tier-3 bridge: B13-CDL certificates -> PIR facts (the in-repo ``pir`` substrate).

This unifies B13 with the PIR evidence substrate delivered in the prior sprint.
Each pipeline certificate becomes a :class:`pir.Fact`, so B13 results gain
content-addressed identity, append-only history, and assumption-taint /
invalidation traversal for free -- instead of B13's parallel certificate format
being the only record.

THE KEY MODELLING DECISION (and why it does not pre-empt the DRAFT sign-off):
B13's `CONDITIONAL(X)` outcome is NOT emitted as a new PIR/SPEC verdict (that
vocabulary extension is still awaiting Erick's sign-off). Instead the
conditioning unknowns X -- exactly the certificate's ``stipulations`` -- become
PIR **assumptions** (`asm:<name>`). The verdict field uses only the SPEC-locked
vocabulary. The payoff is concrete and testable: invalidating `asm:GRH`
downgrades precisely the GRH-conditional facts (Miller PRIME rows), while the
unconditional COMPOSITE facts and the unrelated physics facts are untouched --
which is arguably why CONDITIONAL(X) may not need to be a verdict at all. That
observation is offered for the sign-off discussion; nothing here is filed to
SPEC, the atlas, or the claims table.

If the ``pir`` package is not importable (e.g. B13 extracted and run in
isolation), :func:`available` returns False and callers skip fact emission --
B13's own certificate suite is unaffected.
"""
from __future__ import annotations

import os
import sys

from .common import PKG_ROOT

# The repo root (parent of the b13_cdl package) holds the `pir` package.
_REPO_ROOT = os.path.dirname(PKG_ROOT)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

try:
    import pir  # noqa: E402
    from pir import AnalyzerRef, Fact, FactStore, Warning_  # noqa: E402
    from pir.canonical import content_id  # noqa: E402
    _PIR = True
except Exception:  # pragma: no cover - only when pir is absent
    _PIR = False


def available() -> bool:
    return _PIR


# Per-pipeline mapping to PIR coordinates. Evidence level reflects warrant:
#   exact arithmetic -> E0; interval -> E1; statistical (published sigmas) -> E2;
#   heuristic linearization -> E3 (with a located warning). SOUND passes never
#   claim E3/E4; the HEURISTIC one (ew_vacuum) carries its warning. Verdict uses
#   only the SPEC-locked vocabulary; None where the certificate is a mixed/meta
#   result whose structure lives in `content` (conditionality is in assumptions).
_MAP = {
    "ew_vacuum":         {"evidence": "E3", "verdict": None,             "tag": "HEURISTIC", "layer": "MEASUREMENT", "namespace": "domain"},
    "strong_cp":         {"evidence": "E0", "verdict": "PERMITTED",      "tag": "SOUND",     "layer": "MEASUREMENT", "namespace": "domain"},
    "varying_constants": {"evidence": "E1", "verdict": "REJECTED",       "tag": "SOUND",     "layer": "MEASUREMENT", "namespace": "domain"},
    "grh_miller":        {"evidence": "E0", "verdict": None,             "tag": "SOUND",     "layer": "UNIVERSAL",   "namespace": "invariant"},
    "tunnell_bsd":       {"evidence": "E0", "verdict": None,             "tag": "SOUND",     "layer": "UNIVERSAL",   "namespace": "invariant"},
    "muon_g2":           {"evidence": "E2", "verdict": "NONIDENTIFIABLE", "tag": "SOUND",    "layer": "MEASUREMENT", "namespace": "domain"},
    "h0_tension":        {"evidence": "E2", "verdict": "NONIDENTIFIABLE", "tag": "SOUND",    "layer": "MEASUREMENT", "namespace": "domain"},
    "coverage":          {"evidence": "E0", "verdict": None,             "tag": "SOUND",     "layer": "UNIVERSAL",   "namespace": "analyst"},
}


def _assumptions(cert) -> tuple:
    """The certificate's stipulations ARE its conditioning assumptions."""
    return tuple(f"asm:{s['name']}" for s in cert.get("stipulations", []))


def _measurement_interface(cert, layer) -> tuple:
    """DOMAIN/MEASUREMENT facts must name their declared 𝖬 (SPEC §2). Derive it
    from the stipulation sources (the papers/experiments the verdict rests on)."""
    if layer not in ("DOMAIN", "MEASUREMENT"):
        return ()
    seen, out = set(), []
    for s in cert.get("stipulations", []):
        src = s.get("source")
        if src and src not in seen:
            seen.add(src)
            out.append(src)
    return tuple(out) or (f"stipulated:{cert['pipeline']}",)


def cert_to_fact(cert):
    """Build a :class:`pir.Fact` from a B13 certificate. Fact construction
    enforces PIR's honesty invariants, so this doubles as a validation of the
    soundness->evidence mapping."""
    if not _PIR:
        raise RuntimeError("pir package unavailable; call available() first")
    m = _MAP[cert["pipeline"]]
    warnings = ()
    if cert["soundness"]["tag"] == "HEURISTIC":
        warnings = (Warning_(location=cert["pipeline"],
                             message=cert["soundness"]["warning"]),)
    content = {
        "verdict_string": cert["verdict"],           # original B13 verdict text
        "verdict_detail": cert.get("verdict_detail", {}),
        "witness": cert.get("witness"),
        "entry_id": cert["entry_id"],
    }
    assumptions = _assumptions(cert)
    analyzer = AnalyzerRef(id=f"b13cdl.{cert['pipeline']}", version="0.1.0", tag=m["tag"])
    fact_id = content_id("fct", {
        "content": content, "analyzer": analyzer.to_dict(),
        "assumptions": list(assumptions), "certificate_id": cert["certificate_id"],
    })
    return Fact(
        fact_id=fact_id,
        pir_level="L2",
        evidence_level=m["evidence"],
        layer=m["layer"],
        namespace=m["namespace"],
        status="SUPPORTED",
        analyzer=analyzer,
        content=content,
        created_at=cert["timestamp_utc"],
        assumptions=assumptions,
        measurement_interface=_measurement_interface(cert, m["layer"]),
        source_spans=({"artifact_id": cert["certificate_id"], "span": cert["pipeline"]},),
        warnings=warnings,
        verdict=m["verdict"],
    )


def build_store(certs):
    """Append every certificate's fact into a fresh PIR FactStore."""
    store = FactStore()
    facts = []
    for cert in certs:
        f = cert_to_fact(cert)
        store.add_fact(f)
        facts.append(f)
    return store, facts


def facts_document(certs) -> dict:
    """A single stable-filename artifact: the PIR-fact view over all pipelines."""
    _, facts = build_store(certs)
    return {
        "pir_view_version": "0.1",
        "source": "b13_cdl pipelines -> pir.Fact (Tier-3 bridge)",
        "note": ("CONDITIONAL(X) is modelled as assumption-taint (asm:X), not a "
                 "new verdict; invalidating an assumption downgrades exactly its "
                 "dependent facts."),
        "facts": [f.to_dict() for f in facts],
    }
