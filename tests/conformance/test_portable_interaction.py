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
    materialize_interaction_nodes,
    merge_interaction_headers,
    resolve_fragment_region,
)


def test_shared_fragment_region_authorization() -> None:
    policy = InteractionPolicy(declared_regions=(FragmentRegion(id="main", selector="#main"),))
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


def test_oob_materialize_binds_authorized_id() -> None:
    from hedron_core import Text, render
    from hedron_core.interaction import OobUpdate

    regions = (
        FragmentRegion(id="main", selector="#main"),
        FragmentRegion(id="side", selector="#side"),
    )
    result = InteractionResult(
        content=Text("primary"),
        oob=(OobUpdate(content=Text("side-body"), select="#side"),),
        policy=InteractionPolicy(declared_regions=regions),
    )
    node = materialize_interaction_nodes(result)
    html_out = render(node).html
    assert 'id="side"' in html_out
    assert "hx-swap-oob" in html_out
    assert "side-body" in html_out


def test_oob_select_cannot_authorize_foreign_element_id() -> None:
    from hedron_core import Text
    from hedron_core.interaction import OobUpdate

    regions = (
        FragmentRegion(id="main", selector="#main"),
        FragmentRegion(id="side", selector="#side"),
    )
    with pytest.raises(ValueError, match="must match"):
        authorize_oob_update(
            OobUpdate(content=Text("x"), select="#main", element_id="side"),
            regions=regions,
        )


def test_cache_control_public_rejected_in_extras() -> None:
    with pytest.raises(ValueError, match="public"):
        interaction_headers(
            InteractionResult(
                cache="private",
                headers={"Cache-Control": "public, max-age=60"},
            )
        )


def test_merge_interaction_headers_keeps_typed_hx_redirect() -> None:
    result = InteractionResult(redirect="/safe", cache="private")
    with pytest.raises(ValueError, match="public"):
        merge_interaction_headers(
            result,
            {
                "HX-Redirect": "/evil-overwrite",
                "Cache-Control": "public, max-age=9",
            },
        )
    headers = merge_interaction_headers(
        result,
        {"HX-Redirect": "/evil-overwrite"},
    )
    assert headers["HX-Redirect"] == "/safe"
    assert headers["Cache-Control"] == "private"


def test_vary_headers_portable() -> None:
    headers = interaction_headers(InteractionResult(cache="vary-htmx"))
    assert "HX-Request" in headers["Vary"]
