# EVEZ Self-Audit Findings

## Finding EA-001: Invariant expression execution boundary

Status: PATCHED on this branch.

The legacy Invariance Battery exposes a POST /assert endpoint on service port 9115. The request supplies an invariant expression. The previous implementation passed that expression to Python eval() with a restricted globals dictionary.

That restriction was not a sufficient security boundary. Python expression evaluation is itself an execution surface, and a runtime that claims to enforce invariants must not silently make its assertion language an arbitrary interpreter.

The remediation replaces eval()/exec()-style execution with an explicit AST interpreter. Only a narrow expression language is accepted:

- state lookup
- dictionary get
- approved scalar conversion and aggregate functions
- boolean operators
- arithmetic
- comparisons
- literals and collections

Attribute access other than dictionary get is rejected. Unknown names and calls are rejected. Expression size is capped.

A regression test now scans the service AST and fails if direct eval() or exec() calls are introduced again.

## Epistemic classification

OBSERVED:
- The legacy source contained eval().
- The expression originated from the HTTP assertion request.
- The service listened on 0.0.0.0:9115 in the legacy implementation.

INFERRED:
- The combination created an execution boundary that required stronger isolation than a restricted builtins dictionary alone.

PATCHED:
- The active branch removes the eval() call from the two mirrored Invariance Battery implementations.
- A regression test guards the boundary.

UNKNOWN:
- Whether the historical service was internet reachable.
- Whether anyone actually supplied a malicious expression.
- Whether the historical behavior was exploited.

PROVENANCE != TRUTH.

The finding proves a code-level hazard existed in the historical implementation. It does not prove exploitation occurred.
