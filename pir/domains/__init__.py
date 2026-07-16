"""Domain-specific lowerings: benchmark evidence -> PIR facts.

Stage 2 / P2 of the engineering backlog. Each module here reads a benchmark's
certified evidence and lowers it into PIR L0/L1/L2, re-deriving the benchmark's
verdicts from the stored quantities so the substrate demonstrably *reproduces*
an existing result (never mutating the benchmark's own code or certificate).
"""
