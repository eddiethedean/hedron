"""Pre-release 0.28.2 bugfixes: OOB swap validation, region resolve, select_oob."""

from __future__ import annotations

import pytest

from hedron_core import HtmxLink, InteractionResult, Text, render
from hedron_core.interaction import (
    FragmentRegion,
    InteractionPolicy,
    OobUpdate,
    materialize_interaction_nodes,
    oob_swap,
    resolve_fragment_region,
)


def test_oob_update_rejects_unsafe_swap() -> None:
    with pytest.raises(ValueError, match="Unsafe OobUpdate swap"):
        OobUpdate(content=Text("x"), element_id="panel", swap='innerHTML" onload="alert(1)')
    with pytest.raises(ValueError, match="Unsafe OOB swap"):
        oob_swap("panel", Text("x"), swap="not-a-swap")


def test_resolve_fragment_region_none_is_fail_closed() -> None:
    policy = InteractionPolicy(declared_regions=(FragmentRegion(id="panel", selector="#panel"),))
    assert resolve_fragment_region(policy, None) is None
    assert resolve_fragment_region(policy, "#panel") is not None


def test_materialize_rejects_select_oob_conflict() -> None:
    result = InteractionResult(
        content=Text("main"),
        oob=(OobUpdate(content=Text("nav"), element_id="side-nav"),),
        select_oob="#side-nav",
        policy=InteractionPolicy(
            declared_regions=(FragmentRegion(id="side-nav", selector="#side-nav"),)
        ),
    )
    with pytest.raises(ValueError, match="same-target conflict"):
        materialize_interaction_nodes(result)


def test_materialize_rejects_unparsed_select_oob() -> None:
    with pytest.raises(ValueError, match="simple #id"):
        InteractionResult(
            content=Text("main"),
            oob=(OobUpdate(content=Text("toast"), element_id="hedron-toast"),),
            select_oob="nav.side",
        )
    result = InteractionResult(
        content=Text("main"),
        oob=(OobUpdate(content=Text("toast"), element_id="hedron-toast"),),
    )
    with pytest.raises(ValueError, match="simple #id"):
        materialize_interaction_nodes(result, select_oob="nav.side")


def test_htmx_link_defaults_to_inner_html() -> None:
    html = render(HtmxLink("Go", "/page", target="#main")).html
    assert 'hx-swap="innerHTML"' in html
    assert 'hx-swap="outerHTML"' not in html


def test_htmx_link_rejects_complex_select_oob() -> None:
    with pytest.raises(ValueError, match="simple #id"):
        HtmxLink("Go", "/page", select_oob=".side")


def test_csrf_cookie_secure_shared_helper() -> None:
    from hedron_core.csrf_secure import csrf_cookie_should_be_secure

    assert csrf_cookie_should_be_secure(force_secure=True) is True
    assert csrf_cookie_should_be_secure(force_secure=False) is False
    assert (
        csrf_cookie_should_be_secure(
            request_is_secure=True,
            forwarded_proto_https_trusted=False,
        )
        is True
    )
