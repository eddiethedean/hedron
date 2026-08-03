"""Portable interaction conformance (adapter-agnostic)."""

from __future__ import annotations

import pytest

from hedron_core.htmx_contract import approved_headers
from hedron_core.interaction import (
    FragmentRegion,
    FragmentRegionError,
    InteractionPolicy,
    InteractionResult,
    authorize_oob_update,
    interaction_headers,
    resolve_fragment_region,
)


def test_shared_fragment_region_authorization() -> None:
    policy = InteractionPolicy(
        declared_regions=(FragmentRegion(id="main", selector="#main"),)
    )
    assert resolve_fragment_region(policy, "#main") is not None
    with pytest.raises(FragmentRegionError):
        resolve_fragment_region(policy, "#other")


def test_approved_headers_reject_open_redirect() -> None:
    with pytest.raises(ValueError):
        approved_headers(redirect="https://evil.example/")


def test_interaction_result_oob_region_allowlist() -> None:
    from hedron_core import Text
    from hedron_core.interaction import OobUpdate

    regions = (FragmentRegion(id="side", selector="#side"),)
    authorize_oob_update(OobUpdate(content=Text("x"), select="#side"), regions=regions)
    with pytest.raises(FragmentRegionError):
        authorize_oob_update(OobUpdate(content=Text("x"), select="#nope"), regions=regions)


def test_vary_headers_portable() -> None:
    headers = interaction_headers(InteractionResult(cache="vary-htmx"))
    assert "HX-Request" in headers["Vary"]
