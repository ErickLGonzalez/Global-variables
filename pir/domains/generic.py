"""Generic certificate lowering: any benchmark certificate -> PIR facts.

Completes benchmark coverage. B1/B2/B3 (exact) and B9 (simulation) have bespoke
lowerings that *re-derive* verdicts; this module is the general fallback for the
rest of the suite (B4-B12, M1/M2, the S-layer, atlas, truncation). It is
deliberately conservative and honest:

* it maps a raw status to a SPEC-locked verdict ONLY when the mapping is
  unambiguous (an exact SPEC verdict, or a clear rejection/limitation alias);
  every other domain-specific state (PSD_CERTIFIED, QNEC_STRICT, LHV_COMPATIBLE,
  ...) is preserved verbatim in ``content.raw_status`` with a null verdict —
  never force-fit into the vocabulary;
* evidence level is read from the certificate class (EXACT->E0,
  STATISTICAL/EMPIRICAL->E2, NUMERICAL/DISCOVERY->E3); E3 facts are HEURISTIC and
  carry a located warning;
* ``m_layer_stipulations`` become assumption-taint;
* certificates that phrase no categorical status still yield a fact per result
  section, so every benchmark is represented in the substrate.

Read-only: benchmark code, verdicts, certificates, and the atlas are untouched.
"""

from __future__ import annotations

import json
import os
from typing import Dict, Iterable, List, Tuple

from ..canonical import content_id
from ..models import AnalyzerRef, Fact, Warning_
from ..provenance import FactStore
from ..types import VERDICTS

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Benchmarks with a bespoke lowering (handled elsewhere) — skipped here.
_BESPOKE = {"b1", "b2", "b3", "b9"}

_STATUS_KEYS = ("status", "verdict", "outcome", "psd_status", "fdt_verdict")


def _certificates() -> List[str]:
    out = []
    for fn in sorted(os.listdir(os.path.join(_ROOT, "certificates"))):
        if not fn.endswith(".json"):
            continue
        base = fn[:-len(".json")]
        base = base[:-len("_certificate")] if base.endswith("_certificate") else base
        out.append(base)
    return out


def generic_benchmarks() -> List[str]:
    return [b for b in _certificates() if b not in _BESPOKE and b != "b4_demo"]


def load_certificate(base: str) -> dict:
    for cand in (f"{base}_certificate.json", f"{base}.json"):
        p = os.path.join(_ROOT, "certificates", cand)
        if os.path.exists(p):
            with open(p) as f:
                return json.load(f)
    raise FileNotFoundError(base)


# --- evidence + verdict mapping -------------------------------------------- #
def evidence_of(cert: dict) -> str:
    cls = (str(cert.get("certificate_class", "")) + " "
           + str(cert.get("arithmetic", ""))).upper()
    # Statistical/empirical first: an "exact Clopper-Pearson" interval is still a
    # statistical certificate (the "exact" refers to the interval, not E0).
    if "STATISTICAL" in cls or "EMPIRICAL" in cls or "CLOPPER" in cls:
        return "E2"
    if "EXACT" in cls or "SYMBOLIC" in cls:
        return "E0"
    return "E3"   # NUMERICAL / DISCOVERY / default


def normalize_verdict(raw) -> Tuple[str, str]:
    """(spec_verdict_or_None, raw_string). Only unambiguous mappings promote."""
    if isinstance(raw, bool) or raw is None:
        return None, str(raw)
    s = str(raw)
    u = s.upper()
    if s in VERDICTS:
        return s, s
    if "REJECTED" in u or "VIOLATED" in u or u.startswith("NOT_") or "NOT_A_CHANNEL" in u:
        return "REJECTED", s
    if "LIMITED" in u:
        return "APPARATUS_LIMITED", s
    if u.startswith("FORCED"):
        return "FORCED", s
    if u.startswith("PERMITTED"):
        return "PERMITTED", s
    if u.startswith("NONIDENTIFIABLE"):
        return "NONIDENTIFIABLE", s
    if u.startswith("OBSERVATIONALLY_EQUIVALENT"):
        return "OBSERVATIONALLY_EQUIVALENT", s
    if u.startswith("REPRESENTATION_DEPENDENT"):
        return "REPRESENTATION_DEPENDENT", s
    return None, s


def _find_verdict_nodes(o, path="") -> Iterable[Tuple[str, str, dict]]:
    if isinstance(o, dict):
        for k in _STATUS_KEYS:
            if k in o and isinstance(o[k], (str, bool)):
                yield (path or "root", o[k], o)
                break
        for k, v in o.items():
            yield from _find_verdict_nodes(v, f"{path}.{k}" if path else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _find_verdict_nodes(v, f"{path}[{i}]")


def _witnesses(node: dict) -> Tuple[dict, dict]:
    """Pull any exact witness / impossibility sub-fields from a result node."""
    witness = None
    impossibility = None
    for wk in ("witness", "witness_pivot", "schur_pivots", "recurrence_monic",
               "certified_inner_interval"):
        if wk in node:
            witness = {"kind": wk, "value": node[wk]}
            break
    for ik in ("witness_pivot", "broken_residuals", "impossibility_certificate"):
        if ik in node:
            impossibility = {"kind": ik, "value": node[ik]}
            break
    return witness, impossibility


def lower(base: str) -> List[Fact]:
    cert = load_certificate(base)
    evidence = evidence_of(cert)
    heuristic = evidence in ("E3", "E4")
    tag = "HEURISTIC" if heuristic else "SOUND"
    analyzer = AnalyzerRef(id=f"pir.domains.generic.{base}", version="0.1.0", tag=tag)
    assumptions = tuple(f"asm:{base}_mlayer_{i}"
                        for i, _ in enumerate(cert.get("m_layer_stipulations", [])))
    warn = (Warning_(location=base, message=(
        f"{evidence}: numerical/simulation-conditioned certificate; verdict "
        "depends on the model, not an exact certificate.")),) if heuristic else ()
    mi = (f"cal:{base}_certificate",)

    def mk(subject, verdict, content, witness=None, impossibility=None):
        fid = content_id("fct", {"b": base, "s": subject, "v": verdict, "c": content})
        return Fact(
            fact_id=fid, pir_level="L2", evidence_level=evidence, layer="DOMAIN",
            namespace="domain", status="SUPPORTED", analyzer=analyzer,
            content={"subject": f"{base}:{subject}", **content},
            created_at="1970-01-01T00:00:00Z", assumptions=assumptions,
            measurement_interface=mi, warnings=warn, verdict=verdict,
            witness=witness, impossibility_certificate=impossibility,
            source_spans=({"artifact_id": f"{base}_certificate", "span": subject},))

    facts: List[Fact] = []
    nodes = list(_find_verdict_nodes(cert.get("results", {})))
    seen = set()
    for path, raw, node in nodes:
        if path in seen:
            continue
        seen.add(path)
        verdict, raw_s = normalize_verdict(raw)
        w, imp = _witnesses(node)
        facts.append(mk(path, verdict,
                        {"raw_status": raw_s,
                         "mapped": verdict is not None}, witness=w, impossibility=imp))

    if not facts:
        # No categorical status anywhere: emit one summary fact carrying the
        # certified result sections and headline (verdict null, metrics in content).
        res = cert.get("results", {})
        facts.append(mk("summary", None,
                        {"raw_status": None, "mapped": False,
                         "result_sections": sorted(res.keys()) if isinstance(res, dict) else [],
                         "headline": str(cert.get("headline", ""))[:240]}))
    return facts


def lower_all(benches=None) -> Dict[str, List[Fact]]:
    return {b: lower(b) for b in (benches or generic_benchmarks())}


def suite_store(benches=None) -> FactStore:
    st = FactStore()
    for b, facts in lower_all(benches).items():
        for f in facts:
            st.add_fact(f)
    return st
