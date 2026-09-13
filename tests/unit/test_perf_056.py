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
    samples: list[float] = []
    for _ in range(200):
        start = time.perf_counter()
        SecurityPolicy.from_name("standard")
        compile_trust("/x", TrustPurpose.URL_NAVIGATION)
        RequestBudget().charge("form_fields", 1)
        samples.append((time.perf_counter() - start) * 1000)
    ordered = sorted(samples)
    p95 = ordered[int(round(0.95 * (len(ordered) - 1)))]
    assert p95 <= PERF_CEILINGS["policy_overhead_ms_p95"]
