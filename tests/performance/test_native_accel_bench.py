"""ACCEL-RUST-014 bench: material serialize-stage benefit when native is present."""

from __future__ import annotations

import time

import pytest

from hedron_native import escape_text, escape_text_python, native_available


def _workload(escape_fn: object, rounds: int = 80) -> float:
    payload = ("<" * 8000) + ("&" * 8000) + ("x" * 16000)
    start = time.perf_counter()
    for _ in range(rounds):
        escape_fn(payload)  # type: ignore[operator]
    return time.perf_counter() - start


@pytest.mark.performance
def test_native_escape_material_benefit_when_available() -> None:
    """When the Rust extension loads, require ≥20% faster wall time vs pure Python."""
    if not native_available():
        pytest.skip("hedron-native extension not built in this environment")
    # Warmup plus best-of-three so noisy shared CI CPUs do not hide the benefit.
    _workload(escape_text_python, rounds=4)
    _workload(escape_text, rounds=4)
    py_time = min(_workload(escape_text_python) for _ in range(3))
    native_time = min(_workload(escape_text) for _ in range(3))
    # Material benefit threshold from RFC-0020 / D-048.
    assert native_time < py_time * 0.80, (
        f"native={native_time:.4f}s python={py_time:.4f}s (need ≥20% improvement)"
    )
