"""NATIVE-028: serialize / escape stage benefit when native is loaded."""

from __future__ import annotations

import time

import pytest

from hedron_native import escape_text, escape_text_python, native_available

pytestmark = pytest.mark.performance


def test_native_escape_at_least_20pct_faster_when_loaded() -> None:
    if not native_available():
        pytest.skip("hedron-native extension not loaded")

    # Dense escapable input stresses the hot path.
    sample = ('<&">' * 8000) + ("plain-text-" * 2000)
    rounds = 80

    # Warmup
    for _ in range(3):
        escape_text(sample)
        escape_text_python(sample)

    t0 = time.perf_counter()
    for _ in range(rounds):
        escape_text(sample)
    native_s = time.perf_counter() - t0

    t1 = time.perf_counter()
    for _ in range(rounds):
        escape_text_python(sample)
    python_s = time.perf_counter() - t1

    # Native path must be at least 20% faster than the pure-Python reference.
    assert native_s * 1.20 <= python_s, (
        f"native={native_s:.4f}s python={python_s:.4f}s (need native <= python/1.20)"
    )
