"""REGRESS-040 remediation packet for #162/#203/#204/#219/#220/#222."""

from __future__ import annotations

import pytest

from hedron_core.diagnostics import HedronError
from hedron_core.element_types import ElementFieldOwnership
from hedron_core.registry import register_element_definition, reset_registry_for_tests
from hedron_elements.assets import asset_path as elements_asset_path
from hedron_jinja.inventory import reconcile_csp
from hedron_notebook.preview import NotebookPreview
from hedron_sim.assets import asset_path as sim_asset_path
from hedron_sim.embed import wrap_browser_chrome


def test_issue_162_notebook_iframe_escapes_dimensions() -> None:
    preview = NotebookPreview(host="127.0.0.1", port=9999, token="abc")
    html = preview.iframe_html(width='"><script>alert(1)</script><x y="', height="600")
    assert "<script>" not in html
    assert "&quot;&gt;" in html or "&#x27;" in html or "&lt;" in html or "&quot;" in html


def test_issue_203_style_src_does_not_authorize_inline_script() -> None:
    csp = "default-src 'self'; style-src 'unsafe-inline'; script-src 'self'"
    mismatches = reconcile_csp(csp, required_capabilities=["browser.inline-script"])
    assert mismatches
    mismatches_eval = reconcile_csp(
        "default-src 'self'; style-src 'unsafe-eval'; script-src 'self'",
        required_capabilities=["htmx.eval"],
    )
    assert mismatches_eval


def test_issue_204_sim_caption_is_escaped() -> None:
    html = wrap_browser_chrome("<div>x</div>", caption="</figcaption><script>alert(1)</script>")
    assert "<script>" not in html
    assert "&lt;/figcaption&gt;" in html or "&lt;script&gt;" in html


def test_issue_219_validate_event_detail_rejects_dangerous_own_keys() -> None:
    from pathlib import Path

    bridge = (
        Path(__file__).resolve().parents[2]
        / "packages"
        / "hedron-elements"
        / "src"
        / "hedron_elements"
        / "static"
        / "hedron-bridge.mjs"
    )
    text = bridge.read_text(encoding="utf-8")
    assert 'Object.hasOwn(detail, "__proto__")' in text
    assert "return false" in text


def test_issue_220_asset_path_rejects_escape() -> None:
    with pytest.raises(HedronError):
        elements_asset_path("/etc/passwd")
    with pytest.raises(HedronError):
        elements_asset_path("../plugin.py")
    with pytest.raises(HedronError):
        sim_asset_path("/etc/passwd")
    with pytest.raises(HedronError):
        sim_asset_path("../embed.py")


def test_issue_222_state_ownership_validated_at_registration() -> None:
    reset_registry_for_tests()
    with pytest.raises(HedronError) as exc:
        register_element_definition(
            logical_id="evil",
            tag_name="hedron-evil",
            abi_version=1,
            module_asset_id="x",
            state_ownership=(ElementFieldOwnership(name="csrf_token", mode="local"),),
        )
    assert "HED-ELEMENT-STATE" in str(exc.value)
