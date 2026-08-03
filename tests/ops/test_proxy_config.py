"""Proxy configuration fail-closed."""

from __future__ import annotations

import pytest

from hedron.ops import validate_proxy_trust


def test_empty_forwarded_allow_ips_rejected() -> None:
    with pytest.raises(ValueError, match="forwarded_allow_ips"):
        validate_proxy_trust(trusted_hosts=["a"], forwarded_allow_ips=[])
