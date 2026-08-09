"""BUDGET-025 / W-025-FRAGMENT — fragment latency under HTMX-sized swap load.

Soft CI regression ceiling only — not a published latency SLA. See
``docs/PERFORMANCE_BUDGETS.md`` for normative wording.
"""

from __future__ import annotations

import time

import pytest

from hedron_core import Stack, Text, render
from hedron_core.rendering import RenderMode

pytestmark = pytest.mark.performance

# Soft CI ceiling for a representative fragment (table-sized HTMX swap tree).
_FRAGMENT_MS = 750
_SWAP_NODES = 120


def test_w025_fragment_latency() -> None:
    tree = Stack(*[Text(f"row-{i}") for i in range(_SWAP_NODES)])
    t0 = time.perf_counter()
    html = render(tree, mode=RenderMode.FRAGMENT).html
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert elapsed_ms <= _FRAGMENT_MS
    assert "<html" not in html
    assert "row-0" in html
    assert "row-119" in html
