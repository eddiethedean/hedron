#!/usr/bin/env python3
"""PERF-029: Workbench middleware normalization budget."""

from __future__ import annotations

import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "hedron-workbench" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "hedron" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "hedron-core" / "src"))

from hedron_workbench.config import WorkbenchMode  # noqa: E402
from hedron_workbench.middleware import WorkbenchPathMiddleware  # noqa: E402

# Locked budget: 1000 normalize_scope calls on a typical session path.
# Generous for CI noise; the work is string prefix checks.
BUDGET_P95_MS = 5.0
N = 1000


class _Null:
    async def __call__(self, scope: object, receive: object, send: object) -> None:
        return None


def main() -> int:
    mw = WorkbenchPathMiddleware(_Null(), mode=WorkbenchMode.ON)
    scope = {
        "type": "http",
        "path": "/s/abc/p/1/login",
        "root_path": "/s/abc/p/1",
        "raw_path": b"/s/abc/p/1/login",
        "query_string": b"",
        "method": "GET",
    }
    samples: list[float] = []
    for _ in range(N):
        incoming = dict(scope)
        start = time.perf_counter()
        mw.normalize_scope(incoming)  # type: ignore[arg-type]
        samples.append((time.perf_counter() - start) * 1000)
    p95 = statistics.quantiles(samples, n=20)[18]
    mean = statistics.fmean(samples)

    inactive = WorkbenchPathMiddleware(_Null(), mode=WorkbenchMode.AUTO, active=False)
    inactive_scope = dict(scope)
    inactive_samples: list[float] = []
    for _ in range(N):
        start = time.perf_counter()
        result = inactive.normalize_scope(inactive_scope)  # type: ignore[arg-type]
        inactive_samples.append((time.perf_counter() - start) * 1000)
        assert result is inactive_scope
    inactive_p95 = statistics.quantiles(inactive_samples, n=20)[18]
    print(
        f"PERF-029 normalize_scope n={N} mean_ms={mean:.4f} "
        f"p95_ms={p95:.4f} budget_p95_ms={BUDGET_P95_MS}"
    )
    print(f"PERF-029 inactive_noop p95_ms={inactive_p95:.4f}")
    if max(p95, inactive_p95) > BUDGET_P95_MS:
        print(
            f"PERF-029 budget exceeded: p95 {max(p95, inactive_p95):.4f}ms > {BUDGET_P95_MS}ms",
            file=sys.stderr,
        )
        return 1
    print("ok: PERF-029")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
