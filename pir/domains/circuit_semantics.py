"""Circuit Domain Semantics Module (Stage 2 / P2).

Formalizes how the superconducting-circuit domain (B9) realizes the PIR
abstractions, as four explicit, checkable **contracts**. A domain-semantics
module is what lets a generic PIR lowering stay honest: it says which port
types, act-ops, measurement routes, and compositions are admissible in this
domain, and rejects anything outside them.

Contracts
---------
C1 TYPES        — the circuit port types and their canonical units.
C2 ACT-OPS      — which act-ops the domain realizes, and their physical reading.
C3 MEASUREMENT  — the admissible calibration routes and the promotability rule
                  (the Gibbs route is self-referential and never promotable).
C4 COMPOSITION  — how L1 acts compose into a structural graph (nodes = acts,
                  edges = shared coordinates / couplings), plus the export.

Nothing here re-runs B9 or touches its code; it is the typed contract the
lowering in :mod:`pir.domains.b9` is validated against.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from ..models import Event
from ..types import ACT_OPS


class DomainContractViolation(Exception):
    """Raised when a lowered artifact violates a circuit-domain contract."""


# --- C1 TYPES: circuit port types -> canonical unit ------------------------ #
CIRCUIT_PORT_UNITS: Dict[str, Tuple[str, str]] = {
    # port name family -> (PIR port type, canonical unit)
    "flux":         ("GaugeCoordinate", "Phi0"),
    "charge":       ("GaugeCoordinate", "2e"),
    "current":      ("Observable", "A"),
    "voltage":      ("Observable", "V"),
    "conductance":  ("Coupling", "1/Ohm"),
    "escape_rate":  ("Observable", "1/s"),
    "temperature":  ("ApparatusParameter", "K"),
    "loop_flux":    ("ApparatusParameter", "Phi0"),
    "trajectory":   ("Observable", "1"),
    "ou_drift":     ("Process", "1/s"),
    "equilibrium_state": ("State", "1"),
    "initial_state": ("State", "1"),
}

# --- C2 ACT-OPS the circuit domain realizes -------------------------------- #
CIRCUIT_ACT_OPS: Dict[str, str] = {
    "PREPARE":  "prepare a thermal / ground equilibrium state of the circuit",
    "INTERVENE": "set an apparatus parameter (e.g. loop flux bias)",
    "EVOLVE":   "Langevin/OU dissipative evolution of flux-charge coordinates",
    "MEASURE":  "read an observable (escape rate, trajectory, spectroscopy line)",
    "COARSE_GRAIN": "reduce model order (e.g. 2D -> overdamped 1D)",
    "RECORD":   "record a calibrated run under a declared route",
}

# --- C3 MEASUREMENT routes and promotability ------------------------------- #
# route -> promotable? The Gibbs route infers H_V from the same trajectories it
# audits, so its FDT-consistency is circular and never promotable (B9 T3).
CALIBRATION_ROUTES: Dict[str, bool] = {
    "cal:spectroscopy_route": True,
    "cal:gibbs_route": False,
}


@dataclass(frozen=True)
class StructuralGraph:
    """C4 export: nodes = act events, edges = shared coordinate / ordering."""

    nodes: Tuple[Dict, ...]
    edges: Tuple[Dict, ...]

    def to_dict(self) -> Dict:
        return {"nodes": list(self.nodes), "edges": list(self.edges)}


# --------------------------------------------------------------------------- #
# contract checks                                                             #
# --------------------------------------------------------------------------- #
def check_types(events: List[Event]) -> List[str]:
    """C1: every port a known circuit port with the canonical type+unit."""
    errs = []
    for ev in events:
        for p in ev.ports:
            spec = CIRCUIT_PORT_UNITS.get(p.name)
            if spec is None:
                errs.append(f"{ev.event_id}: unknown circuit port {p.name!r}")
                continue
            want_type, want_unit = spec
            if p.type != want_type:
                errs.append(f"{ev.event_id}.{p.name}: type {p.type} != {want_type}")
            if p.unit != want_unit:
                errs.append(f"{ev.event_id}.{p.name}: unit {p.unit} != {want_unit}")
    return errs


def check_act_ops(events: List[Event]) -> List[str]:
    """C2: every act-op is one the circuit domain realizes (and a valid PIR op)."""
    errs = []
    for ev in events:
        if ev.op not in ACT_OPS:
            errs.append(f"{ev.event_id}: {ev.op} not a PIR act-op")
        elif ev.op not in CIRCUIT_ACT_OPS:
            errs.append(f"{ev.event_id}: {ev.op} not realized in the circuit domain")
    return errs


def is_promotable_route(route: str) -> bool:
    """C3: whether a calibration route yields promotable evidence."""
    if route not in CALIBRATION_ROUTES:
        raise DomainContractViolation(f"unknown calibration route {route!r}")
    return CALIBRATION_ROUTES[route]


def check_measurement(events: List[Event]) -> List[str]:
    """C3: any MEASURE/RECORD act must cite a known calibration route."""
    errs = []
    for ev in events:
        if ev.op in ("MEASURE", "RECORD"):
            routes = ev.calibration_route or []
            if not routes:
                errs.append(f"{ev.event_id}: {ev.op} act cites no calibration route")
            for rt in routes:
                if rt not in CALIBRATION_ROUTES:
                    errs.append(f"{ev.event_id}: unknown calibration route {rt!r}")
    return errs


def structural_graph(events: List[Event]) -> StructuralGraph:
    """C4: build the structural graph. Nodes are acts; a directed edge joins
    consecutive acts by ordering_index (the time thread), and any two acts that
    share a port name get an (undirected-style) coordinate edge."""
    nodes = tuple({"id": ev.event_id, "op": ev.op,
                   "ports": [p.name for p in ev.ports],
                   "order": ev.timing.get("ordering_index")}
                  for ev in events)
    ordered = sorted(events, key=lambda e: e.timing.get("ordering_index", 0))
    edges = []
    for a, b in zip(ordered, ordered[1:]):
        edges.append({"from": a.event_id, "to": b.event_id, "kind": "time"})
    for i, a in enumerate(events):
        pa = {p.name for p in a.ports}
        for b in events[i + 1:]:
            shared = pa & {p.name for p in b.ports}
            for name in sorted(shared):
                edges.append({"from": a.event_id, "to": b.event_id,
                              "kind": "coordinate", "via": name})
    return StructuralGraph(nodes=nodes, edges=tuple(edges))


def validate(events: List[Event]) -> List[str]:
    """Run all four contracts; return a flat list of violations (empty = ok)."""
    return (check_types(events) + check_act_ops(events)
            + check_measurement(events))
