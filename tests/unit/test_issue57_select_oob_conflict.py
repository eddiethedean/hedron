"""Issue #57: select_oob + OobUpdate same-target conflict helpers and check."""

from __future__ import annotations

import pytest

from hedron_core import render
from hedron_core.codes import HED_HTMX_0002
from hedron_core.interaction import (
    FragmentRegion,
    InteractionPolicy,
    InteractionResult,
    OobUpdate,
    conflicting_select_oob_targets,
    materialize_interaction_nodes,
    oob_swap,
    parse_select_oob_element_ids,
)


def test_parse_and_conflict_helper() -> None:
    assert parse_select_oob_element_ids("#side-nav, #toast") == frozenset(
        {"side-nav", "toast"}
    )
    oob = (
        OobUpdate(content="nav", element_id="side-nav", swap="innerHTML"),
        OobUpdate(content="x", element_id="other"),
    )
    assert conflicting_select_oob_targets("#side-nav", oob) == frozenset({"side-nav"})
    assert conflicting_select_oob_targets(None, oob) == frozenset()
    assert conflicting_select_oob_targets("#toast", oob) == frozenset()


def test_oob_swap_tag_is_defense_in_depth() -> None:
    html = render(oob_swap("side-nav", "Profile", swap="innerHTML", tag="nav")).html
    assert html.startswith("<nav")
    assert 'id="side-nav"' in html
    assert 'hx-swap-oob="innerHTML"' in html
    with pytest.raises(ValueError, match="Unsupported"):
        oob_swap("side-nav", "x", tag="article")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Unsupported"):
        OobUpdate(content="x", element_id="side-nav", tag="article")  # type: ignore[arg-type]


def test_materialize_honors_oob_update_tag() -> None:
    regions = (FragmentRegion(id="side-nav", selector="#side-nav"),)
    result = InteractionResult(
        content=None,
        oob=(OobUpdate(content="kids", element_id="side-nav", swap="innerHTML", tag="nav"),),
        policy=InteractionPolicy(declared_regions=regions),
    )
    node = materialize_interaction_nodes(result)
    assert node is not None
    html = render(node).html
    assert "<nav" in html
    assert 'id="side-nav"' in html


def test_check_detects_select_oob_oobupdate_conflict(tmp_path) -> None:
    from hedron.cli import _check_select_oob_conflicts

    bad = tmp_path / "shell.py"
    bad.write_text(
        """
from hedron import HtmxLink, InteractionResult, OobUpdate, Text

link = HtmxLink(
    "Profile",
    "/profile",
    target="#main-panel",
    select="#main-panel",
    select_oob="#side-nav",
)

result = InteractionResult(
    content=Text("main"),
    oob=(OobUpdate(content=Text("nav"), element_id="side-nav", swap="innerHTML"),),
)
""",
        encoding="utf-8",
    )
    diags = _check_select_oob_conflicts(tmp_path)
    assert any(d.code == HED_HTMX_0002 for d in diags)
    assert any("side-nav" in d.explanation for d in diags)

    good = tmp_path / "shell_ok.py"
    good.write_text(
        """
from hedron import HtmxLink, InteractionResult, OobUpdate, Text

link = HtmxLink("Profile", "/profile", target="#main-panel", select="#main-panel")
result = InteractionResult(
    content=Text("main"),
    oob=(OobUpdate(content=Text("nav"), element_id="side-nav", swap="innerHTML"),),
)
""",
        encoding="utf-8",
    )
    # Only the conflicting file should warn; rewrite project to good-only.
    bad.unlink()
    diags_ok = _check_select_oob_conflicts(tmp_path)
    assert not any(d.code == HED_HTMX_0002 for d in diags_ok)
