"""Regression coverage for bounded authentication rate-limit state (#795)."""

from __future__ import annotations

from hedron.security.auth_rate_limit import AuthRateLimiter


def test_rate_limiter_fails_closed_at_key_budget() -> None:
    limiter = AuthRateLimiter(limit=1, window_seconds=60, max_keys=1)

    assert limiter.check("victim", "/login", now=0) == (True, 0)
    assert limiter.check("victim", "/login", now=1) == (False, 59)
    assert limiter.check("attacker", "/login", now=2) == (False, 58)
    assert limiter.check("victim", "/login", now=3) == (False, 57)

    assert len(limiter._events) == 1
    assert limiter._key("victim", "/login") in limiter._events
    assert limiter._key("attacker", "/login") not in limiter._events


def test_rate_limiter_prunes_expired_buckets_without_full_scan() -> None:
    limiter = AuthRateLimiter(limit=2, window_seconds=10, max_keys=100)
    for index in range(50):
        assert limiter.check(f"client-{index}", "/login", now=0) == (True, 0)
    assert len(limiter._events) == 50

    limiter.check("fresh", "/login", now=10)
    assert len(limiter._events) == 1
    assert limiter._key("fresh", "/login") in limiter._events
