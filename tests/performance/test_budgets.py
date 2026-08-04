"""Phase 0.8 performance budget enforcement."""

from __future__ import annotations

import json
import time

import pytest

from hedron_core import Page, Stack, Text, render
from hedron_core._serializer import serialize_tree
from hedron_core.diagnostics import DiagnosticSeverity, diagnostics_to_json, make_diagnostic
from hedron_core.rendering import RenderContext, RenderMode, _normalize, _RenderState

pytestmark = pytest.mark.performance


def test_render_stage_budgets() -> None:
    tree = Stack(*[Text(f"item-{i}") for i in range(200)])
    ctx = RenderContext.standalone()
    state = _RenderState(ctx)

    t0 = time.perf_counter()
    nodes = _normalize(tree, state, depth=0)
    t1 = time.perf_counter()
    html = serialize_tree(nodes)
    t2 = time.perf_counter()
    full = render(tree).html
    t3 = time.perf_counter()

    assert (t1 - t0) * 1000 <= 250
    assert (t2 - t1) * 1000 <= 250
    assert (t3 - t0) * 1000 <= 500
    assert len(html.encode("utf-8")) <= 100 * 1024
    assert "item-0" in full


def test_page_and_fragment_payload_budgets() -> None:
    page = Page(Text("hello"), title="Budget")
    page_html = render(page, mode=RenderMode.PAGE).html
    frag_html = render(Stack(*[Text(f"n{i}") for i in range(200)]), mode=RenderMode.FRAGMENT).html
    assert len(page_html.encode("utf-8")) <= 200 * 1024
    assert len(frag_html.encode("utf-8")) <= 100 * 1024
    assert "<html" in page_html
    assert "<html" not in frag_html


def test_diagnostic_payload_budget() -> None:
    diags = [
        make_diagnostic(
            f"HED-TEST-{i:04d}",
            severity=DiagnosticSeverity.INFORMATION,
            title="budget",
            explanation="x" * 200,
            remediation="y" * 100,
        )
        for i in range(20)
    ]
    payload = json.dumps(diagnostics_to_json(diags)).encode("utf-8")
    assert len(payload) <= 256 * 1024
