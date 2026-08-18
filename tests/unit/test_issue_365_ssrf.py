"""#365: map proxy SSRF blocks CGNAT and other non-global IPs."""

from __future__ import annotations

import pytest

from hedron_core import HedronError
from hedron_maps.proxy import assert_ssrf_safe
from hedron_maps.spec import MapPolicy


def test_proxy_blocks_cgnat_and_benchmark_ranges() -> None:
    for host in ("100.64.0.1", "198.18.0.1"):
        policy = MapPolicy(allowed_origins=(f"https://{host}",))
        with pytest.raises(HedronError):
            assert_ssrf_safe(f"https://{host}/t", policy, resolve_dns=False)
