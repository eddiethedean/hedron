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
    assert parse_select_oob_element_ids("#side-nav, #toast") == frozenset({"side-nav", "toast"})
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
    from hedron_core.diagnostics import DiagnosticSeverity

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
    assert any(d.severity is DiagnosticSeverity.ERROR for d in diags if d.code == HED_HTMX_0002)
    assert any("side-nav" in d.explanation for d in diags)

    hx = tmp_path / "hx_form.py"
    hx.write_text(
        """
from hedron_core import Form, InteractionResult, OobUpdate, Text

form = Form(Text("x"), action="/save", select_oob="#toast")
result = InteractionResult(
    content=Text("main"),
    oob=(OobUpdate(content=Text("t"), element_id="toast"),),
)
""",
        encoding="utf-8",
    )
    diags_hx = _check_select_oob_conflicts(tmp_path)
    assert any("toast" in d.explanation for d in diags_hx)

    complex_sel = tmp_path / "complex.py"
    complex_sel.write_text(
        """
link_attrs = {"hx-select-oob": "nav.side"}
""",
        encoding="utf-8",
    )
    diags_complex = _check_select_oob_conflicts(tmp_path)
    assert any(
        d.code == HED_HTMX_0002 and d.severity is DiagnosticSeverity.WARNING for d in diags_complex
    )

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
    bad.unlink()
    hx.unlink()
    complex_sel.unlink()
    diags_ok = _check_select_oob_conflicts(tmp_path)
    assert not any(d.code == HED_HTMX_0002 for d in diags_ok)


def test_oob_default_swap_is_inner_html() -> None:
    html = render(oob_swap("side-nav", "Profile")).html
    assert 'hx-swap-oob="innerHTML"' in html
    assert OobUpdate(content="x", element_id="side-nav").swap == "innerHTML"


def test_unparsed_select_oob_tokens() -> None:
    from hedron_core.interaction import unparsed_select_oob_tokens

    assert unparsed_select_oob_tokens("#ok, nav.side") == frozenset({"nav.side"})
    assert unparsed_select_oob_tokens("#ok") == frozenset()
