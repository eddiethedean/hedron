"""Ops health/readiness/shutdown tests."""

from __future__ import annotations

import pytest

from hedron.ops import (
    ShutdownRegistry,
    liveness,
    readiness,
    redacted_log_extra,
    validate_proxy_trust,
)
from hedron_core.adapter import LifecycleResource


def test_liveness_and_readiness() -> None:
    assert liveness()["status"] == "ok"
    code, body = readiness({"cache": lambda: True, "jobs": lambda: False})
    assert code == 503
    assert body["checks"]["jobs"] == "down"


def test_redaction() -> None:
    extra = redacted_log_extra({"user": "a", "password": "secret", "token": "t"})
    assert extra["password"] == "[redacted]"
    assert extra["user"] == "a"


def test_proxy_fail_closed() -> None:
    with pytest.raises(ValueError):
        validate_proxy_trust(trusted_hosts=[], forwarded_allow_ips=None)
    validate_proxy_trust(trusted_hosts=["example.com"], forwarded_allow_ips=None)


def test_shutdown_order() -> None:
    reg = ShutdownRegistry()
    order: list[str] = []
    reg.register(LifecycleResource("a", order=10), lambda: order.append("a"))
    reg.register(LifecycleResource("b", order=20), lambda: order.append("b"))
    assert reg.shutdown() == ["b", "a"]
