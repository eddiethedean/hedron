"""Non-blocking performance foundation benchmarks."""

from __future__ import annotations

import time

import pytest

from hedron_core import Stack, Text, render
from hedron_core._serializer import serialize_tree
from hedron_core.rendering import RenderContext, _normalize, _RenderState


@pytest.mark.performance
def test_tree_vs_serialize_baselines() -> None:
    tree = Stack(*[Text(f"item-{i}") for i in range(200)])
    ctx = RenderContext.standalone()
    state = _RenderState(ctx)

    t0 = time.perf_counter()
    nodes = _normalize(tree, state, depth=0)
    t1 = time.perf_counter()
    _ = serialize_tree(nodes)
    t2 = time.perf_counter()

    build_ms = (t1 - t0) * 1000
    serialize_ms = (t2 - t1) * 1000
    # Soft ceiling for CI smoke; not a release budget.
    assert build_ms < 500
    assert serialize_ms < 500
    # Full render still works.
    assert "item-0" in render(tree).html
