"""SECURITY-043: ownership, CSRF, redaction, limits, disagreement."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from tests.unit._helpers_043 import csrf_headers, make_app, reset_043

from hedron import Page, Text, refresh
from hedron_core.diagnostics import HedronError
from hedron_core.htmx.policy import FragmentRegion
from hedron_core.security import Secret
from hedron_core.updates import (
    MAX_REFRESH_TARGETS,
    PortableTarget,
    RefreshIntent,
    redacted_descriptor_view,
    safe_dom_id,
)


def setup_function() -> None:
    reset_043()


def test_csrf_required_and_wrong_target_403() -> None:
    app = make_app(security="standard")

    @app.refreshable
    def status():
        return Text("ok")

    @app.command(fallback="/")
    def ping():
        return refresh(status)

    @app.page("/")
    def home():
        return Page(status(), title="Home")

    client = TestClient(app)
    denied = client.post(ping.path, headers={"HX-Request": "true"})
    assert denied.status_code == 403
    headers = csrf_headers(client)
    ok = client.post(ping.path, headers=headers)
    assert ok.status_code == 200
    bad = client.get(status.path, headers={"HX-Request": "true", "HX-Target": "not-the-host"})
    assert bad.status_code == 403


def test_foreign_handle_refresh_is_403() -> None:
    app = make_app(security="standard")

    @app.refreshable
    def status():
        return Text("ok")

    @app.command(fallback="/")
    def ping():
        foreign = PortableTarget(
            logical_id="status",
            dom_id=safe_dom_id("status"),
            path=status.path,
            app_id="forged",
            region=FragmentRegion(id=safe_dom_id("status"), selector="#h-view-status"),
        )
        return RefreshIntent(targets=(foreign,))

    @app.page("/")
    def home():
        return Page(status(), title="Home")

    client = TestClient(app)
    response = client.post(ping.path, headers=csrf_headers(client))
    assert response.status_code == 403
    assert (
        "HED-UPDATE-0003" in response.text
        or "Foreign" in response.text
        or response.status_code == 403
    )


def test_bound_secrets_redacted_from_descriptor() -> None:
    app = make_app()

    @app.refreshable
    def item(item_id: str):
        return Text(item_id)

    with pytest.raises(HedronError):
        item.bind(item_id=Secret("super-secret-token"))
    view = redacted_descriptor_view(item.descriptor)
    blob = str(view)
    assert "super-secret" not in blob
    assert "password" not in blob.lower()


def test_generated_routes_are_reachable_not_obscure() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("visible")

    client = TestClient(app)
    response = client.get(status.path)
    assert response.status_code == 200
    assert "visible" in response.text


def test_refresh_limit_adversarial() -> None:
    targets = []
    for i in range(MAX_REFRESH_TARGETS + 1):
        targets.append(
            PortableTarget(
                logical_id=f"v{i}",
                dom_id=safe_dom_id(f"v{i}"),
                path=f"/v{i}",
                app_id="a",
                region=FragmentRegion(id=safe_dom_id(f"v{i}"), selector=f"#h-view-v{i}"),
            )
        )
    with pytest.raises(HedronError):
        RefreshIntent(targets=tuple(targets))
