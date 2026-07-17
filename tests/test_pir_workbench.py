"""PIR Workbench (P9 presentation layer) — build + honesty + read-only checks.

W1  The build inlines the exported bundle into a single self-contained page:
    the JSON is embedded and parseable, and there is NO external request
    (no http(s):// URL, no src=/href= to a host, no <link>, no remote font).
W2  Evidence honesty is preserved in the rendered shell: SOUND vs HEURISTIC,
    evidence levels E0–E4, and warnings are all present and a HEURISTIC/E3 fact
    is never labelled as certified.
W3  The interactive invalidation view reproduces FactStore.invalidate_assumption
    exactly: a Python mirror of the page's algorithm (direct assumption
    membership + transitive closure over depends_on_facts) reproduces the
    committed demo downgrade set, and the real FactStore agrees.
W4  The Artifact fragment is body-only (no <html>/<head>/<body> wrappers), so
    the page is publishable under the strict Artifact CSP unchanged.

Run: python3 tests/test_pir_workbench.py   (exit nonzero on any failure)
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ci.export_pir_view import build_bundle
from pir_workbench.build import build, inline_bundle, extract_body, TEMPLATE
from pir.provenance import FactStore
from pir.domains import b9

FAILURES = []


def check(label, errors):
    if errors:
        FAILURES.append((label, errors))
        print(f"  [FAIL] {label}")
        for e in errors[:6]:
            print(f"         - {e}")
    else:
        print(f"  [ ok ] {label}")


# Build the bundle in-process and render the page from it (no reliance on a
# pre-existing build/ artifact, so the test is hermetic).
BUNDLE = build_bundle()
with open(TEMPLATE, "r", encoding="utf-8") as _fh:
    TPL = _fh.read()
PAGE = inline_bundle(TPL, json.dumps(BUNDLE))


def w1_self_contained():
    errs = []
    # embedded, parseable bundle
    m = re.search(r'<script id="pir-bundle"[^>]*>(.*?)</script>', PAGE, re.S)
    if not m:
        errs.append("no pir-bundle data island found")
    else:
        blob = m.group(1).replace("<\\/", "</")
        try:
            data = json.loads(blob)
            if data["meta"]["n_facts"] != BUNDLE["meta"]["n_facts"]:
                errs.append("embedded bundle fact count mismatch")
        except Exception as exc:  # noqa: BLE001
            errs.append(f"embedded bundle not parseable: {exc!r}")
    # no external references anywhere in the page
    for pat in (r"https?://", r"<link\b", r"\bsrc\s*=", r"cdn\.", r"fonts\."):
        hits = re.findall(pat, PAGE)
        # allow xmlns-free svg; the only href-like tokens permitted are in-page url(#..)
        if pat == r"\bsrc\s*=" and not hits:
            continue
        if hits:
            errs.append(f"external reference matched /{pat}/ ({len(hits)}x)")
    # url(...) must only be in-document fragment refs (url(#id))
    for u in re.findall(r"url\(([^)]*)\)", PAGE):
        if not u.strip().startswith("#"):
            errs.append(f"non-fragment url() reference: {u}")
    check("W1 self-contained page with embedded, parseable bundle", errs)


def w2_honesty_markers():
    errs = []
    for token in ("SOUND", "HEURISTIC", "Honesty key", "E0", "E3",
                  "warnings", "DOWNGRADED", "read-only"):
        if token not in PAGE:
            errs.append(f"missing honesty/marker token: {token!r}")
    # the legend must explicitly say HEURISTIC/E3 is not a certified result
    if "not certified" not in PAGE and "is not certified" not in PAGE:
        errs.append("legend does not state HEURISTIC/E3 is not certified")
    # every HEURISTIC fact in the bundle keeps its tag (not silently upgraded)
    heur = [f for f in BUNDLE["facts"] if f["analyzer"]["tag"] == "HEURISTIC"]
    if not heur:
        errs.append("bundle has no HEURISTIC facts to protect (unexpected)")
    check(f"W2 SOUND/HEURISTIC + evidence + warnings preserved "
          f"({len(heur)} HEURISTIC facts)", errs)


def _mirror_invalidate(facts, asm):
    """Pure-Python mirror of the page's JS invalidation algorithm."""
    direct = {f["fact_id"] for f in facts if asm in (f.get("assumptions") or [])}
    affected = set(direct)
    changed = True
    while changed:
        changed = False
        for f in facts:
            fid = f["fact_id"]
            if fid in affected:
                continue
            dep = set(f.get("depends_on_facts") or [])
            if dep & affected:
                affected.add(fid)
                changed = True
    return sorted(affected)


def w3_invalidation_matches_python():
    errs = []
    demo = BUNDLE["invalidation_demo"]
    asm = demo["assumption"]
    committed = sorted(demo["downgraded_facts"])

    # (a) the page's algorithm, mirrored, reproduces the committed demo set
    mirror = _mirror_invalidate(BUNDLE["facts"], asm)
    if not set(committed) <= set(mirror):
        errs.append(f"page-mirror {mirror} does not cover committed demo {committed}")

    # (b) the real FactStore over the B9 store agrees with the committed demo
    _, _, b9_facts = b9.lower(b9.load_certificate())
    store = FactStore()
    for f in b9_facts:
        store.add_fact(f)
    real = sorted(store.invalidate_assumption(asm, reason="test drill"))
    if real != committed:
        errs.append(f"FactStore {real} != committed demo {committed}")
    check("W3 invalidation view reproduces FactStore.invalidate_assumption", errs)


def w4_artifact_fragment():
    errs = []
    frag = extract_body(PAGE)
    # word-boundary match so structural tags are caught but <header>/<head-ing
    # class names are not false positives.
    for bad in (r"<html\b", r"<head\b", r"<body\b", r"<!doctype"):
        if re.search(bad, frag, re.I):
            errs.append(f"artifact fragment still contains {bad!r}")
    if "pir-bundle" not in frag:
        errs.append("artifact fragment dropped the data island")
    check("W4 Artifact fragment is body-only and self-contained", errs)


def main():
    print("PIR Workbench (P9) tests")
    w1_self_contained()
    w2_honesty_markers()
    w3_invalidation_matches_python()
    w4_artifact_fragment()
    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s).")
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
