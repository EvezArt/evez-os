# DESA-S Opaque-Domain Benchmark

This benchmark checks protocol behavior without supplying a predefined domain adapter.

It verifies that:

1. a temporary domain representation is induced from opaque observations;
2. entity conflict is detected without automatic promotion to VERIFIED;
3. the targeter appears in its own target space;
4. rejected candidates survive inside the selection receipt;
5. the DESA-S state is serializable as EVEZ;
6. the same state can be carried as an EVEX accountable transition;
7. unsupported epistemic promotion remains blocked.

Run:

    PYTHONPATH=. python3 benchmarks/desas-socratious/self_test.py
    PYTHONPATH=. python3 benchmarks/desas-socratious/verify_evex.py

Expected output:

    PASS DESA-S Opaque-Domain Benchmark v1
    PASS DESA-S EVEX interoperability fixture v1

The benchmark tests controller and protocol behavior. It does not establish general intelligence, consciousness, or universal zero-shot domain competence.
