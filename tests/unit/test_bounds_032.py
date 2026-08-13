"""BOUNDS-032 coverage."""

from __future__ import annotations

import time

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


def test_cancelled_ids_cap_and_ttl_evict() -> None:
    bounds = McpBounds(max_cancelled=3, cancel_ttl_seconds=0.05)
    for i in range(5):
        bounds.request_cancel(str(i))
    assert len(bounds._cancelled) == 3
    assert "0" not in bounds._cancelled
    assert "1" not in bounds._cancelled
    assert bounds.is_cancelled("4")

    time.sleep(0.06)
    assert bounds.is_cancelled("4") is False
    assert "4" not in bounds._cancelled


def test_sessions_cap_and_ttl_evict() -> None:
    bounds = McpBounds(max_sessions=2, session_ttl_seconds=0.05)
    bounds.open_session("s0", principal="p", origin=None)
    bounds.open_session("s1", principal="p", origin=None)
    bounds.open_session("s2", principal="p", origin=None)
    assert bounds.session("s0") is None
    assert bounds.session("s1") is not None
    assert bounds.session("s2") is not None
    assert len(bounds._sessions) == 2

    time.sleep(0.06)
    assert bounds.session("s2") is None
    assert len(bounds._sessions) == 0


def test_rate_buckets_delete_empty_and_cap_principals() -> None:
    bounds = McpBounds(max_rate_principals=2, rate_window_seconds=0.05)
    bounds.check_rate("user-0")
    bounds.check_rate("user-1")
    bounds.check_rate("user-2")
    assert "user-0" not in bounds._rate_buckets
    assert set(bounds._rate_buckets) == {"user-1", "user-2"}

    time.sleep(0.06)
    bounds.check_rate("user-3")
    assert "user-1" not in bounds._rate_buckets
    assert "user-2" not in bounds._rate_buckets
    assert set(bounds._rate_buckets) == {"user-3"}
