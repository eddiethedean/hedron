# Phase 0.63 upgrade fixtures

The 0.63 tooling formats are independently versioned and fail closed on unknown
schemas. A `hedron.interaction-trace.v2` payload is rejected by the decoder;
0.60–0.62 theme packages remain accepted by the published
`>=0.60,<0.64` compatibility range. Disabling inspection, profiling, checks, or
migration changes no runtime rendering or server authority.

The compatibility fixture is exercised by `tests/unit/test_phase063_release_evidence.py`.
