"""Reference application static render tests."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from hedron_core import HedronError, SafeUrl, TrustedHtml, UrlPurpose, html, render

_APP_PATH = Path(__file__).resolve().parent / "app.py"
_SPEC = importlib.util.spec_from_file_location("reference_app", _APP_PATH)
assert _SPEC and _SPEC.loader
_MOD = importlib.util.module_from_spec(_SPEC)
sys.modules["reference_app"] = _MOD
_SPEC.loader.exec_module(_MOD)

render_page = _MOD.render_page
render_users_fragment = _MOD.render_users_fragment
team_admin_page = _MOD.team_admin_page


def test_reference_page_renders_offline() -> None:
    result = render_page()
    assert result.html.startswith("<!DOCTYPE html>")
    assert "Team Admin" in result.html
    assert "Ada Lovelace" in result.html
    assert 'action="/users"' in result.html
    assert "Create user" in result.html


def test_reference_fragment_renders() -> None:
    result = render_users_fragment()
    assert "<table>" in result.html
    assert "Grace Hopper" in result.html
    assert "<!DOCTYPE" not in result.html


def test_unsafe_raw_html_rejected() -> None:
    with pytest.raises(HedronError):
        render(html.raw("<script>alert(1)</script>"))  # type: ignore[arg-type]


def test_unsafe_url_rejected_in_page_context() -> None:
    with pytest.raises(HedronError):
        SafeUrl.parse("javascript:alert(1)", purpose=UrlPurpose.NAVIGATION)


def test_trusted_html_allowed_explicitly() -> None:
    node = html.raw(TrustedHtml.reviewed("<em>reviewed</em>", source="reference-app-test"))
    assert render(node).html == "<em>reviewed</em>"


def test_form_errors_surface() -> None:
    page = team_admin_page(form_errors=("Name is required",))
    html_out = render(page).html
    assert "Name is required" in html_out
    assert 'role="alert"' in html_out
