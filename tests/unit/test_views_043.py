"""VIEW-043: @app.refreshable, FragmentHandle, bind, hosts."""

from __future__ import annotations

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from tests.unit._helpers_043 import make_app, reset_043

from hedron import BoundFragment, FragmentHandle, Page, Text
from hedron_core.codes import HED_VIEW_0002, HED_VIEW_0003, HED_VIEW_0004
from hedron_core.diagnostics import HedronError
from hedron_core.rendering import render


def setup_function() -> None:
    reset_043()


def test_refreshable_returns_handle_and_generated_route() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("live")

    @app.page("/")
    def home():
        return Page(status(), title="Home")

    assert isinstance(status, FragmentHandle)
    assert status.path == "/_hedron/views/status"
    assert status.logical_id == "status"
    assert status.method == "GET"
    assert status.renderer is status.__wrapped__
    assert status.renderer_signature is not None
    markup = render(status()).html
    assert 'id="h-view-status"' in markup
    assert 'hx-get="/_hedron/views/status"' in markup
    client = TestClient(app)
    page = client.get("/")
    assert page.status_code == 200
    assert "live" in page.text
    assert "hedron:refresh-h-view-status" in page.text
    frag = client.get(
        status.path,
        headers={"HX-Request": "true", "HX-Target": status.dom_id},
    )
    assert frag.status_code == 200
    assert "live" in frag.text
    missing = client.get(status.path, headers={"HX-Request": "true"})
    assert missing.status_code == 200
    disagree = client.get(
        status.path,
        headers={"HX-Request": "true", "HX-Target": "evil"},
    )
    assert disagree.status_code == 403


def test_fragment_decorator_still_returns_function() -> None:
    app = make_app()
    region = app.region("legacy", description="legacy panel")

    @app.fragment("/legacy", region=region)
    def legacy():
        return Text("legacy")

    assert callable(legacy) and not isinstance(legacy, FragmentHandle)


def test_explicit_path_key_and_openapi_hidden() -> None:
    app = make_app()

    @app.refreshable("/status-panel", key="StatusPanel", include_in_schema=True)
    def named():
        return Text("panel")

    assert named.path == "/status-panel"
    assert named.logical_id == "StatusPanel"
    schema = app.openapi()
    assert "/status-panel" in schema["paths"]
    hidden = make_app()

    @hidden.refreshable
    def secret_view():
        return Text("nope")

    openapi = hidden.openapi()
    assert secret_view.path not in openapi.get("paths", {})


def test_bind_is_structural_and_get_authoritative() -> None:
    app = make_app()

    @app.refreshable
    def item(item_id: str, q: str = "all"):
        return Text(f"{item_id}:{q}")

    with pytest.raises(HedronError) as unbound:
        item()
    assert unbound.value.diagnostic.code == HED_VIEW_0003
    bound = item.bind(item_id="42", q="hot")
    assert isinstance(bound, BoundFragment)
    assert bound.path.startswith("/_hedron/views/item/42")
    assert "q=hot" in bound.path
    assert bound.dom_id.startswith("h-view-item-")
    assert "42" not in bound.dom_id
    # Bound secrets must not appear raw in identity.
    from hedron_core.security import Secret

    with pytest.raises(HedronError) as secret:
        item.bind(item_id=Secret("tok"))  # type: ignore[arg-type]
    assert secret.value.diagnostic.code == HED_VIEW_0004
    with pytest.raises(HedronError) as extra:
        item.bind(item_id="1", unknown="x")
    assert extra.value.diagnostic.code == HED_VIEW_0004
    client = TestClient(app)
    response = client.get(
        "/_hedron/views/item/42",
        headers={"HX-Request": "true", "HX-Target": bound.dom_id},
        params={"q": "hot"},
    )
    assert response.status_code == 200
    assert "42:hot" in response.text
    assert f'id="{bound.dom_id}"' in response.text
    assert f"hedron:refresh-{bound.dom_id}" in response.text
    assert "{item_id}" not in response.text
    assert 'hx-get="/_hedron/views/item/42?q=hot"' in response.text
    path_only = item.bind(item_id="42")
    default_q = client.get(
        "/_hedron/views/item/42",
        headers={"HX-Request": "true", "HX-Target": path_only.dom_id},
    )
    assert default_q.status_code == 200
    assert f'id="{path_only.dom_id}"' in default_q.text
    assert path_only.dom_id != bound.dom_id
    assert "{item_id}" not in default_q.text
    assert 'hx-get="/_hedron/views/item/42"' in default_q.text


def test_duplicate_unbound_mounts_fail() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("x")

    with pytest.raises(HedronError) as page_err:
        render(Page(status(), status(), title="Home"))
    assert page_err.value.diagnostic.code == HED_VIEW_0002


def test_generic_arity_is_two_slots() -> None:
    assert len(FragmentHandle.__parameters__) == 2
    first, second = FragmentHandle.__parameters__
    assert "bind" in first.__name__.lower()
    assert "content" in second.__name__.lower()


def test_sync_async_depends_and_docs_preserved() -> None:
    app = make_app()

    def dep() -> str:
        return "d"

    @app.refreshable
    async def async_status(flag: str = Depends(dep)):
        """Documented view."""
        return Text(flag)

    assert async_status.renderer.__doc__ == "Documented view."
    client = TestClient(app)
    response = client.get(
        async_status.path,
        headers={"HX-Request": "true", "HX-Target": async_status.dom_id},
    )
    assert response.status_code == 200
    assert "d" in response.text
