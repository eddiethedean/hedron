"""BOUNDS-032 coverage."""

from __future__ import annotations

import pytest

from hedron_mcp import BoundsError, McpBounds, McpProjection


def test_size_rate_concurrency_cancel() -> None:
    bounds = McpBounds(max_request_bytes=8, max_concurrency=1, rate_limit_per_minute=2)
    with pytest.raises(BoundsError, match="max_request_bytes"):
        bounds.check_size("0123456789")
    bounds.check_rate("alice")
    bounds.check_rate("alice")
    with pytest.raises(BoundsError, match="rate"):
        bounds.check_rate("alice")
    bounds.acquire()
    with pytest.raises(BoundsError, match="concurrency"):
        bounds.acquire()
    bounds.release()
    rid = bounds.new_request_id()
    bounds.request_cancel(rid)
    assert bounds.is_cancelled(rid)
    bounds.open_session("s1", principal="alice", origin="https://app.example")
    assert bounds.session("s1")["principal"] == "alice"
    bounds.close_session("s1")
    assert bounds.session("s1") is None


def test_multi_worker_shared_prefix_required() -> None:
    projection = McpProjection(enabled=True, bounds=McpBounds(shared_prefix=""))
    with pytest.raises(BoundsError, match="shared_prefix"):
        projection.bounds.assert_worker_safe()
    projection.bounds.shared_prefix = "hedron-mcp"
    projection.bounds.assert_worker_safe()
