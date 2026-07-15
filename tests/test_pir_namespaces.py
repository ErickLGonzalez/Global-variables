"""PIR namespace-discipline tests (Stage 1, hard constraint #6).

Positive:
  N1  Same-namespace dependency needs no transform; a declared, typed transform
      legalizes a cross-namespace (even promoting) dependency.
Negative (required):
  N2  Illegal namespace promotion without a transform record -> reject
      (effective: -> global: with no transform).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pir import (
    AnalyzerRef, Fact, FactStore, IllegalNamespacePromotion, NamespaceTransform,
)
from pir.namespaces import is_promotion, require_transform
from pir.types import Namespace, PassTag


def _fact(fid, namespace, depends=()):
    return Fact(
        fact_id=fid, pir_level="L2", evidence_level="E0", layer="UNIVERSAL",
        namespace=namespace, status="SUPPORTED",
        analyzer=AnalyzerRef("A", "0.1.0", PassTag.SOUND),
        content={"n": fid}, created_at="2026-07-15T12:00:00Z",
        depends_on_facts=tuple(depends),
        source_spans=({"artifact_id": "art", "span": "s"},),
    )


def n1_legal_transform():
    st = FactStore()
    # same namespace: no transform needed.
    st.add_fact(_fact("e0", "effective"))
    st.add_fact(_fact("e1", "effective", depends=("e0",)))
    # cross-namespace promotion WITH a typed transform: allowed.
    st.add_fact(_fact("eff", "effective"))
    tr = NamespaceTransform(
        name="RG_fixed_point", from_namespace=Namespace.effective,
        to_namespace=Namespace.global_,
        type_signature="effective->global via scale-independent fixed point",
    )
    assert tr.is_promotion() and is_promotion(Namespace.effective, Namespace.global_)
    st.add_fact(_fact("glob", "global", depends=("eff",)),
                edge_transforms={"eff": tr})
    assert "glob" in st
    print("N1 legal transform: PASS  same-namespace dependency free; "
          "effective→global legalized by a typed RG_fixed_point transform")
    return {"ok": True}


def n2_illegal_promotion():
    st = FactStore()
    st.add_fact(_fact("eff", "effective"))
    # promotion effective -> global with NO transform: reject.
    try:
        st.add_fact(_fact("glob", "global", depends=("eff",)))
        assert False, "illegal promotion accepted"
    except IllegalNamespacePromotion as e:
        assert "illegal promotion" in str(e)
    # a transform declaring the WRONG endpoints is also rejected.
    wrong = NamespaceTransform("bad", Namespace.domain, Namespace.global_, "x")
    try:
        st.add_fact(_fact("glob2", "global", depends=("eff",)),
                    edge_transforms={"eff": wrong})
        assert False, "mismatched transform accepted"
    except IllegalNamespacePromotion as e:
        assert "but the reference is" in str(e)
    # direct unit check of the guard.
    try:
        require_transform(Namespace.effective, Namespace.global_, None)
        assert False
    except IllegalNamespacePromotion:
        pass
    print("N2 illegal promotion: PASS  effective→global without a transform "
          "rejected; endpoint-mismatched transform rejected")
    return {"ok": True}


if __name__ == "__main__":
    r1 = n1_legal_transform(); r2 = n2_illegal_promotion()
    print("\nALL PIR NAMESPACE TESTS PASS (N1-N2)")
