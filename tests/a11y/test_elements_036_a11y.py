"""A11Y-036: fallback/upgraded semantic checks (automated)."""

from __future__ import annotations

from hedron_core.rendering import render
from hedron_elements.example import Example


def test_pre_upgrade_has_accessible_name_hooks() -> None:
    html = render(Example(status="Online")).html
    assert "Online" in html
    assert "Details" in html  # toggle label present in SSR
    assert 'type="button"' in html


def test_server_region_readable_without_js() -> None:
    html = render(Example(status="Degraded")).html
    assert 'data-hedron-server-region="content"' in html
    assert "Degraded" in html
