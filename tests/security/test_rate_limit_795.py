"""Regression coverage for bounded authentication rate-limit state (#795)."""

from __future__ import annotations

from hedron.security.auth_rate_limit import AuthRateLimiter


def test_rate_limiter_evicts_oldest_bucket_at_key_budget() -> None:
    limiter = AuthRateLimiter(limit=2, window_seconds=60, max_keys=2)

    assert limiter.check("first", "/login", now=0) == (True, 0)
    assert limiter.check("second", "/login", now=1) == (True, 0)
    assert limiter.check("third", "/login", now=2) == (True, 0)

    assert len(limiter._events) == 2
    assert limiter._key("first", "/login") not in limiter._events
    assert limiter._key("second", "/login") in limiter._events
    assert limiter._key("third", "/login") in limiter._events


def test_rate_limiter_prunes_expired_buckets_without_full_scan() -> None:
    limiter = AuthRateLimiter(limit=2, window_seconds=10, max_keys=100)
    for index in range(50):
        assert limiter.check(f"client-{index}", "/login", now=0) == (True, 0)
    assert len(limiter._events) == 50

    limiter.check("fresh", "/login", now=10)
    assert len(limiter._events) == 1
    assert limiter._key("fresh", "/login") in limiter._events
