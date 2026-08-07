"""Phase 0.20 EVAL-020: reject hx-vals/hx-headers js: on Python html.*."""

from __future__ import annotations

import pytest

from hedron_core import allow_htmx_eval, html
from hedron_core.diagnostics import HedronError
from hedron_core.htmx_eval import hx_value_needs_eval


def test_hx_vals_js_rejected_by_default() -> None:
    with pytest.raises(HedronError) as exc:
        html.div(**{"hx-vals": "js:{a:1}"})
    assert exc.value.diagnostic.code == "HED-SEC-0011"


def test_hx_headers_js_rejected_by_default() -> None:
    with pytest.raises(HedronError) as exc:
        html.div(**{"hx-headers": "js:{"})
    assert exc.value.diagnostic.code == "HED-SEC-0011"


def test_json_hx_vals_allowed() -> None:
    node = html.div(**{"hx-vals": '{"a": 1}'})
    assert node.attributes["hx-vals"] == '{"a": 1}'


def test_allow_htmx_eval_opt_in() -> None:
    with allow_htmx_eval():
        node = html.div(**{"hx-vals": "js:{a:1}"})
    assert "js:" in str(node.attributes["hx-vals"])


def test_smuggled_js_prefix_detected() -> None:
    assert hx_value_needs_eval("hx-vals", " { js:1 }")
    assert hx_value_needs_eval("hx-vals", "JS:alert(1)")
    assert not hx_value_needs_eval("hx-vals", '{"js": 1}')
