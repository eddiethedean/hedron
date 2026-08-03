"""Phase 0.3 HDN compiler tests."""

from __future__ import annotations

import pytest

from hedron_core import HedronError, Text, TrustedHtml, compile_hdn, format_hdn, render, run_program
from hedron_core.hdn.expr import eval_expr
from hedron_core.rendering import RenderMode


def test_hdn_basic_html_and_expr() -> None:
    result = compile_hdn('<p class="x">Hello {name}</p>')
    nodes = run_program(result.program, {"name": "Ada"})
    html = render(nodes, mode=RenderMode.FRAGMENT).html
    assert "Hello Ada" in html
    assert 'class="x"' in html


def test_hdn_if_else_for() -> None:
    source = """
{#if show}
  <span>yes</span>
{:else}
  <span>no</span>
{/if}
<ul>
{#for item in items}
  <li>{item}</li>
{/for}
</ul>
"""
    prog = compile_hdn(source).program
    html = render(
        run_program(prog, {"show": True, "items": ["a", "b"]}),
        mode=RenderMode.FRAGMENT,
    ).html
    assert "yes" in html
    assert "no" not in html
    assert "<li>a</li>" in html
    assert "<li>b</li>" in html


def test_hdn_component_tag() -> None:
    source = "<Text content={label} />"
    prog = compile_hdn(source).program
    nodes = run_program(prog, {"label": "Hi"}, components={"Text": Text})
    html = render(nodes, mode=RenderMode.FRAGMENT).html
    assert "Hi" in html


def test_hdn_trusted_html_required() -> None:
    prog = compile_hdn("{@html payload}").program
    with pytest.raises(HedronError) as exc:
        run_program(prog, {"payload": "<b>x</b>"})
    assert exc.value.diagnostic.code == "HED-HDN-0006"

    nodes = run_program(
        prog,
        {"payload": TrustedHtml.reviewed("<b>ok</b>", source="test")},
    )
    html = render(nodes, mode=RenderMode.FRAGMENT).html
    assert "<b>ok</b>" in html


def test_hdn_rejects_imports_and_calls() -> None:
    with pytest.raises(HedronError):
        eval_expr("__import__('os').system('x')", {})
    with pytest.raises(HedronError):
        eval_expr("open('x')", {})


def test_hdn_formatter_idempotent() -> None:
    source = """<div>
<span>Hi {name}</span>
</div>
"""
    once = format_hdn(source)
    twice = format_hdn(once)
    assert once == twice


def test_hdn_nullish_and_helpers() -> None:
    assert eval_expr("missing ?? 'fallback'", {"missing": None}) == "fallback"
    assert eval_expr("len(items)", {"items": [1, 2, 3]}) == 3
    assert eval_expr("str(n)", {"n": 7}) == "7"


def test_hdn_source_map_present() -> None:
    result = compile_hdn("<p>{name}</p>")
    assert result.source_map
    assert result.program.format_version == 1
