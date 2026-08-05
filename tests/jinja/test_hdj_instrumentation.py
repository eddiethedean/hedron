"""HDJ-DEF-014: loop/macro budgets, extension evidence, helpers, a11y, portable fixtures."""

from __future__ import annotations

import pytest
from jinja2 import DictLoader, Environment

from hedron_core import RenderMode
from hedron_core.diagnostics import HedronError
from hedron_jinja import (
    ExtensionEvidence,
    ExtensionRegistry,
    HdjContext,
    HedronJinja,
    LoopMacroBudget,
    a11y_static_diagnostics,
    checker_fixture_from_diagnostics,
    instrumentation_session,
    portable_checker_json,
    record_loop_iteration,
    record_macro_call,
)


def _hdj(body: str, *, features: str = "") -> str:
    feature_line = f'features = ["{features}"]\n' if features else ""
    return (
        f'---hdj\nversion = 1\nkind = "fragment"\nprofile = "standard"\n{feature_line}---\n{body}'
    )


def test_loop_macro_budget_enforced() -> None:
    with instrumentation_session(LoopMacroBudget(max_loop_iterations=3, max_macro_calls=2)):
        record_loop_iteration(2)
        record_macro_call(1)
        with pytest.raises(HedronError) as loop_exc:
            record_loop_iteration(2)
        assert loop_exc.value.diagnostic.code == "HED-JINJA-0031"
    with instrumentation_session(LoopMacroBudget(max_loop_iterations=10, max_macro_calls=1)):
        with pytest.raises(HedronError) as macro_exc:
            record_macro_call(2)
        assert macro_exc.value.diagnostic.code == "HED-JINJA-0032"


def test_render_records_loop_via_global() -> None:
    source = _hdj("{{ hedron_record_loop(1) }}ok")
    templates = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": source})),
        max_loop_iterations=10,
    )
    assert "ok" in templates.render("x.hdj", {}).html


def test_extension_evidence_required_for_hx_ext() -> None:
    source = _hdj('<div hx-ext="sse">x</div>')
    bare = HedronJinja(Environment(loader=DictLoader({"x.hdj": source})))
    codes = {d.code for d in bare.check("x.hdj")}
    assert "HED-JINJA-0030" in codes

    registry = ExtensionRegistry()
    registry.register(
        ExtensionEvidence(
            extension_id="sse",
            version="2.0.0",
            digest=ExtensionRegistry.digest_bytes(b"sse"),
            csp={"script-src": "'self'"},
            load_order=1,
            kind="htmx",
        )
    )
    ok = HedronJinja(
        Environment(loader=DictLoader({"y.hdj": source})),
        extension_registry=registry,
    )
    codes_ok = {d.code for d in ok.check("y.hdj") if d.code == "HED-JINJA-0030"}
    assert not codes_ok


def test_scoped_style_and_validate_attr_helpers() -> None:
    ctx = HdjContext(mode=RenderMode.FRAGMENT, locale="en", theme=None)
    assert ctx.scoped_style("--hedron-gap: 1rem") == "--hedron-gap: 1rem"
    with pytest.raises(ValueError):
        ctx.scoped_style("color: red")
    assert ctx.validate_attr("class", "x") == 'class="x"'
    with pytest.raises(ValueError):
        ctx.validate_attr("onclick", "alert(1)")


def test_a11y_static_diagnostics() -> None:
    diags = a11y_static_diagnostics(
        template_name="x.hdj",
        body='<img src="/a.png"><button></button><div id="a"></div><span id="a"></span>',
    )
    titles = {d.title for d in diags}
    assert "img missing alt" in titles
    assert "Duplicate HTML id" in titles
    assert "button missing accessible name" in titles


def test_portable_checker_fixture_sarif_shaped() -> None:
    diags = a11y_static_diagnostics(template_name="x.hdj", body="<img src=x>")
    payload = checker_fixture_from_diagnostics(fixture_id="a11y-img", diagnostics=diags)
    assert payload["format"] == "sarif-shaped-v1"
    assert payload["runs"][0]["results"]
    assert "HED-JINJA-0033" in portable_checker_json(diags)
