"""ACTIONSTATE-037: InteractionState module and action-async element."""

from __future__ import annotations

from pathlib import Path

from hedron_core.rendering import render
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_elements.action_async import ActionAsync


def test_interaction_state_module_exists() -> None:
    static = (
        Path(__file__).resolve().parents[2] / "packages/hedron-elements/src/hedron_elements/static"
    )
    module = static / "interaction-state.mjs"
    assert module.is_file()
    text = module.read_text(encoding="utf-8")
    assert "InteractionState" in text
    assert "idle" in text
    assert "pending" in text


def test_action_async_ssr_button_and_hx_post() -> None:
    html = render(
        ActionAsync("Run", hx_post=SafeUrl.parse("/run", purpose=UrlPurpose.NAVIGATION))
    ).html
    assert "hedron-action-async" in html
    assert 'type="button"' in html
    assert "Run" in html
    assert 'hx-post="/run"' in html
    assert 'data-hedron-server-region="control"' in html
