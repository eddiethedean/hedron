"""Additive class_ theme hooks on content/control builtins (#29)."""

from __future__ import annotations

from hedron_core import (
    Alert,
    Badge,
    Button,
    Heading,
    IconButton,
    LinkButton,
    Status,
    SubmitButton,
    Text,
    render,
)


def test_button_appends_host_classes() -> None:
    html = render(Button("Save", variant="primary", class_="button button-primary")).html
    assert 'class="hedron-button hedron-button-primary button button-primary"' in html


def test_link_submit_icon_button_class_() -> None:
    assert "host-link" in render(LinkButton("Go", "/go", class_="host-link")).html
    assert "hedron-button hedron-button-secondary" in render(LinkButton("Go", "/go")).html
    assert "host-submit" in render(SubmitButton("Send", class_="host-submit")).html
    assert "host-icon" in render(IconButton("Close", icon="×", class_="host-icon")).html


def test_text_and_heading_class_() -> None:
    text = render(Text("Controlled access", as_="p", class_="eyebrow")).html
    assert 'class="hedron-text eyebrow"' in text
    assert "<p" in text
    heading = render(Heading("Title", level=2, class_="page-title")).html
    assert 'class="hedron-heading page-title"' in heading
    # Without class_, keep markup free of forced theme hooks.
    assert "class=" not in render(Text("plain")).html


def test_alert_badge_status_class_() -> None:
    alert = render(Alert("Saved", tone="success", class_="alert alert-success")).html
    assert 'class="hedron-alert hedron-alert-success alert alert-success"' in alert
    badge = render(Badge("New", tone="info", class_="chip")).html
    assert 'class="hedron-badge hedron-badge-info chip"' in badge
    status = render(Status("Ready", class_="status-pill")).html
    assert 'class="hedron-status hedron-status-info status-pill"' in status
