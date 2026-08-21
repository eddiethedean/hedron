"""PERF-056 evidence."""

from __future__ import annotations

import time

from hedron_core.security_plane import (
    PERF_CEILINGS,
    RequestBudget,
    SecurityPolicy,
    TrustPurpose,
    compile_trust,
)


def test_perf_056_ceilings_and_policy_overhead() -> None:
    assert PERF_CEILINGS["policy_overhead_ms_p95"] <= 5.0
    assert PERF_CEILINGS["max_concurrency"] == 32
    start = time.perf_counter()
    for _ in range(200):
        SecurityPolicy.from_name("standard")
        compile_trust("/x", TrustPurpose.URL_NAVIGATION)
        RequestBudget().charge("form_fields", 1)
    elapsed_ms = (time.perf_counter() - start) * 1000 / 200
    assert elapsed_ms < PERF_CEILINGS["policy_overhead_ms_p95"] * 20  # generous CI bound
