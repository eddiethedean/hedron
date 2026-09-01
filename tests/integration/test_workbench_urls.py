"""URL-029: Hedron mount/redirect/CSRF/cookie composition under Workbench."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi import WebSocket
from fastapi.testclient import TestClient
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Receive, Scope, Send

from hedron import (
    Form,
    Hedron,
    Page,
    RefreshButton,
    Stack,
    SubmitButton,
    Text,
    ToastHost,
    html,
    redirect_local,
    refresh,
    resolve_mount_path_from_environ,
    swap,
)
from hedron.mount import prefix_local_path
from hedron_core import reset_registry_for_tests
from hedron_posit import HedronPosit, WorkbenchConfig, workbenchify
from hedron_posit.urls import connect_external_base_from_request, mounted_redirect


@pytest.fixture(autouse=True)
def _fresh_registry() -> None:
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    yield


class _RootPathInjector:
    """Simulate Workbench/proxy: HTTP path includes mount and ASGI root_path is set."""

    def __init__(self, app: Callable[[Scope, Receive, Send], Awaitable[None]], mount: str) -> None:
        self.app = app
        self.mount = mount

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") in {"http", "websocket"}:
            scope = dict(scope)
            scope["root_path"] = self.mount
        await self.app(scope, receive, send)


def _app(*, mount: str = "/s/demo/p/9"):
    app = Hedron(
        title="wb",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
        root_path=mount,
    )
    region = app.region("status", description="status")

    @app.page("/")
    def home() -> Page:
        return Page(Text("home"), title="Home")

    @app.page("/login")
    def login() -> Page:
        return Page(Text("login"), title="Login")

    @app.fragment("/status", region=region)
    def status():
        return swap(Text("ok"))

    @app.action("/ping", method="POST")
    def ping() -> Page:
        return Page(Text("pong"), title="Pong")

    @app.page("/go")
    def go():
        return redirect_local("/login")

    return workbenchify(app, mode="on"), region


def test_constructor_root_path_scopes_csrf_cookie() -> None:
    app, _ = _app()
    client = TestClient(_RootPathInjector(app, "/s/demo/p/9"))
    response = client.get("/s/demo/p/9/")
    assert response.status_code == 200
    set_cookie = response.headers.get("set-cookie", "")
    assert "Path=/s/demo/p/9" in set_cookie or "path=/s/demo/p/9" in set_cookie.lower()


def test_env_export_before_construction(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HEDRON_ROOT_PATH", "/s/env/p/1")
    assert resolve_mount_path_from_environ() is not None
    app = Hedron(
        title="wb",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
    )
    assert app.state.hedron_mount_path == "/s/env/p/1"
    assert app.state.hedron_cookie_path == "/s/env/p/1"


def test_workbench_facade_needs_no_wrapper() -> None:
    app = HedronPosit(
        title="facade",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
        workbench=WorkbenchConfig(mount="/s/facade/p/3"),
    )

    @app.page("/")
    def home() -> Page:
        return Page(Text("facade"), title="Facade")

    client = TestClient(app)
    response = client.get("/s/facade/p/3/")
    assert response.status_code == 200
    assert "facade" in response.text
    assert app.state.hedron_cookie_path == "/s/facade/p/3"
    assert workbenchify(app) is app
    assert app.workbench_status()["normalizer_count"] == 1


def test_workbench_facade_explicit_root_path_wins() -> None:
    app = HedronPosit(
        title="facade",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
        root_path="/explicit",
        workbench=WorkbenchConfig(mount="/s/facade/p/3"),
    )
    assert app.state.hedron_mount_path == "/explicit"
    assert app.hedron_workbench.browser_mount == "/explicit"


def test_workbench_facade_full_stack_without_scope_injector() -> None:
    mount = "/s/native/p/5"
    app = HedronPosit(
        title="native",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
        workbench_mount=mount,
    )
    region = app.region("native-status", description="native status")

    @app.page("/")
    def native_home() -> Page:
        return Page(Text("native-home"), title="Home")

    @app.fragment("/status", region=region)
    def native_status():
        return swap(Text("native-ok"))

    @app.action("/ping", method="POST")
    def native_ping() -> Page:
        return Page(Text("native-pong"), title="Pong")

    @app.websocket("/ws")
    async def native_socket(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text("native-ws")
        await websocket.close()

    client = TestClient(app)
    home = client.get(f"{mount}/")
    assert home.status_code == 200
    assert "Path=/s/native/p/5" in home.headers.get("set-cookie", "")
    token = home.cookies.get("hedron_csrf")
    assert token
    fragment = client.get(
        f"{mount}/status",
        headers={"HX-Request": "true", "HX-Target": f"#{region.id}"},
    )
    assert fragment.status_code == 200
    assert "native-ok" in fragment.text
    posted = client.post(f"{mount}/ping", headers={"X-CSRF-Token": token})
    assert posted.status_code == 200
    assert client.get(f"{mount}/hedron-static/hedron-default.css").status_code == 200
    assert client.get(f"{mount}/openapi.json").status_code == 200
    with client.websocket_connect(f"{mount}/ws") as websocket:
        assert websocket.receive_text() == "native-ws"


def test_rendered_component_urls_are_automatically_mounted_once() -> None:
    mount = "/s/rendered/p/7"
    app = HedronPosit(
        title="rendered",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
        workbench_mount=mount,
    )
    region = app.region("rendered-status", description="rendered status")

    @app.page("/")
    def mounted_controls() -> Page:
        return Page(
            RefreshButton.for_region(region, href="/status", label="Refresh"),
            Form(SubmitButton("Send"), action="/ping", method="post"),
            title="Mounted controls",
        )

    response = TestClient(app).get(f"{mount}/")
    assert response.status_code == 200
    assert f'hx-get="{mount}/status"' in response.text
    assert f'action="{mount}/ping"' in response.text
    assert response.text.count(f"{mount}{mount}") == 0
    assert f'name="hedron-mount-path" content="{mount}"' in response.text
    assert f'src="{mount}/hedron-static/hedron-mount.mjs"' in response.text


def test_workbench_handle_controls_refresh_and_post_without_full_page_navigation() -> None:
    mount = "/s/guide/p/8000"
    app = HedronPosit(
        title="guide",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
        workbench_mount=mount,
    )

    @app.view("/status")
    def guide_status():
        return html.div(Text("All systems operational"), role="status")

    @app.action("/ping", fallback="/")
    def guide_ping():
        return refresh(guide_status).toast("pong")

    @app.page("/")
    def guide_home() -> Page:
        return Page(
            Stack(
                guide_status(),
                guide_status.refresh_button("Refresh status"),
                guide_ping.button("Ping"),
                ToastHost(),
            ),
            title="Guide",
        )

    client = TestClient(app, follow_redirects=False)
    page = client.get(f"{mount}/")
    token = page.cookies.get("hedron_csrf")
    assert page.status_code == 200
    assert token
    assert f'hx-get="{mount}/status"' in page.text
    assert f'hx-post="{mount}/ping"' in page.text
    assert "hx-headers" in page.text
    assert 'id="hedron-toast"' in page.text

    fragment = client.get(
        f"{mount}/status",
        headers={"HX-Request": "true", "HX-Target": guide_status.dom_id},
    )
    assert fragment.status_code == 200
    assert "All systems operational" in fragment.text

    action = client.post(
        f"{mount}/ping",
        headers={"HX-Request": "true", "X-CSRF-Token": token},
    )
    assert action.status_code == 200
    assert "HX-Trigger" in action.headers
    assert action.headers.get("HX-Reswap") == "none"
    assert "hedron-toast" in action.text
    assert "pong" in action.text

    fallback = client.post(f"{mount}/ping", data={"csrf_token": token})
    assert fallback.status_code == 303
    assert fallback.headers["location"] == f"{mount}/"


def test_request_time_root_path_adapts_urls_redirects_and_owned_cookies() -> None:
    mount = "/content/runtime"
    app = HedronPosit(
        title="runtime",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
    )

    @app.page("/")
    def runtime_home() -> Page:
        return Page(Form(SubmitButton("Send"), action="/ping", method="post"), title="Runtime")

    @app.page("/go")
    def runtime_go():
        return redirect_local("/login")

    client = TestClient(_RootPathInjector(app, mount))
    home = client.get(f"{mount}/")
    assert home.status_code == 200
    assert f'action="{mount}/ping"' in home.text
    assert f"Path={mount}" in home.headers.get("set-cookie", "")
    redirect = client.get(f"{mount}/go", follow_redirects=False)
    assert redirect.headers["location"] == f"{mount}/login"
    assert app.state.hedron_cookie_path == "/"


def test_connect_contract_leaves_one_outer_response_rebase(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("POSIT_PRODUCT", "CONNECT")
    mount = "/content/runtime"
    app = HedronPosit(
        title="connect-runtime",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
    )

    @app.page("/")
    def connect_home(request: Request) -> Page:
        request.session["probe"] = "ok"
        return Page(
            Form(SubmitButton("Send"), action="/ping", method="post"),
            title="Runtime",
        )

    @app.page("/go")
    def connect_go():
        return redirect_local("/login")

    client = TestClient(_RootPathInjector(app, mount))
    headers = {"RStudio-Connect-App-Base-URL": f"https://connect.example{mount}"}
    home = client.get(f"{mount}/", headers=headers)
    assert f'action="{mount}/ping"' in home.text
    owned = [
        value
        for value in home.headers.get_list("set-cookie")
        if value.startswith(("hedron_csrf=", "session="))
    ]
    assert len(owned) == 2
    assert all("path=/;" in value.lower() for value in owned)
    assert all(mount not in value for value in owned)

    redirect = client.get(f"{mount}/go", headers=headers, follow_redirects=False)
    assert redirect.headers["location"] == f"{mount}/login"


def test_htmx_redirect_header_is_automatically_mounted() -> None:
    mount = "/s/headers/p/4"
    app = HedronPosit(
        title="headers",
        security="development",
        explorer="off",
        session_secret="test-secret-ok",
        workbench_mount=mount,
    )

    @app.get("/hx")
    def hx_redirect():
        return Response(headers={"HX-Redirect": "/next"})

    response = TestClient(app).get(f"{mount}/hx")
    assert response.headers["hx-redirect"] == f"{mount}/next"


def test_inactive_workbench_facade_matches_plain_hedron(monkeypatch: pytest.MonkeyPatch) -> None:
    # Generic hosting variables must not opt the subclass into Workbench behavior.
    monkeypatch.setenv("HOST", "public.example")
    monkeypatch.setenv("PORT", "99999")
    monkeypatch.setenv("BASE_PATH", "/generic-platform")
    app = HedronPosit(
        title="ordinary",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
    )

    @app.page("/")
    def ordinary_home() -> Page:
        return Page(Text("ordinary-home"), title="Home")

    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "ordinary-home" in response.text
    assert app.state.hedron_mount_path == ""
    assert app.state.hedron_cookie_path == "/"
    assert app.hedron_workbench.active is False


def test_inactive_facade_preserves_generic_asgi_root_path() -> None:
    app = HedronPosit(
        title="ordinary-mount",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
        root_path="/ordinary",
    )

    @app.page("/")
    def ordinary_mounted_home() -> Page:
        return Page(Text("ordinary-mounted"), title="Home")

    response = TestClient(_RootPathInjector(app, "/ordinary")).get("/ordinary/")
    assert response.status_code == 200
    assert "ordinary-mounted" in response.text
    assert "Path=/ordinary" in response.headers.get("set-cookie", "")
    assert app.hedron_workbench.active is False


def test_explicit_workbench_root_overrides_stale_hedron_mount(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HEDRON_ROOT_PATH", "/stale")
    app = HedronPosit(
        title="root",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
        workbench_mount="/",
    )
    assert app.state.hedron_mount_path == ""
    assert app.state.hedron_cookie_path == "/"


def test_workbench_status_redacts_session_mount() -> None:
    session_id = "4566a3c9ab5a7ad01e1a7"
    app = HedronPosit(
        title="status",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
        workbench_mount=f"/s/{session_id}/p/9",
    )
    assert session_id not in str(app.workbench_status())


def test_redirect_uses_mount_once() -> None:
    app, _ = _app()
    client = TestClient(_RootPathInjector(app, "/s/demo/p/9"))
    response = client.get("/s/demo/p/9/go", follow_redirects=False)
    assert response.status_code in {303, 307, 302}
    location = response.headers.get("location", "")
    assert location == "/s/demo/p/9/login"
    assert location.count("/s/demo/p/9") == 1


def test_mounted_redirect_helper() -> None:
    response = mounted_redirect("/admin", mount="/s/abc/p/1")
    assert response.headers["location"] == "/s/abc/p/1/admin"


def test_workbench_public_base_emits_scheme_absolute_location() -> None:
    mount = "/s/demo/p/8000"
    app = HedronPosit(
        title="absolute-location",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
        workbench_mount=mount,
        workbench_public_base_url=f"http://127.0.0.1:8787{mount}",
    )

    @app.page("/login")
    def login() -> Page:
        return Page(Text("login"), title="Login")

    @app.page("/go")
    def go():
        return redirect_local("/login")

    response = TestClient(app).get(f"{mount}/go", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == f"{mount}/login"


def test_absolute_redirect_helper_uses_trusted_workbench_base() -> None:
    mount = "/s/demo/p/8000"
    app = HedronPosit(
        title="absolute-helper",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
        workbench_mount=mount,
        workbench_public_base_url=f"http://127.0.0.1:8787{mount}",
    )

    @app.page("/login")
    def login() -> Page:
        return Page(Text("login"), title="Login")

    @app.page("/go")
    def go():
        return app.redirect("/login", absolute=True)

    response = TestClient(app).get(f"{mount}/go", follow_redirects=False)
    assert response.headers["location"] == f"http://127.0.0.1:8787{mount}/login"


def test_launcher_resolved_loopback_base_emits_absolute_location(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mount = "/s/docker-session/p/8000"
    monkeypatch.setenv("HEDRON_WORKBENCH_RESOLVED_MOUNT", mount)
    monkeypatch.setenv(
        "HEDRON_WORKBENCH_RESOLVED_PUBLIC_BASE",
        f"http://127.0.0.1:8787{mount}",
    )
    monkeypatch.setenv("HEDRON_WORKBENCH_RESOLVED_MODE", "on")
    monkeypatch.setenv("HEDRON_WORKBENCH_RESOLVED_SOURCE", "rserver-url")
    app = HedronPosit(
        title="resolved-absolute-location",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
    )

    @app.page("/go")
    def go():
        return redirect_local("/login")

    response = TestClient(app).get(f"{mount}/go", follow_redirects=False)
    assert response.headers["location"] == f"{mount}/login"


def test_prefix_assets_once() -> None:
    assert prefix_local_path("/hedron-static/htmx.js", "/s/demo/p/9") == (
        "/s/demo/p/9/hedron-static/htmx.js"
    )
    assert (
        prefix_local_path("/s/demo/p/9/hedron-static/htmx.js", "/s/demo/p/9").count("/s/demo/p/9")
        == 1
    )


def test_mode_off_parity_with_plain_hedron() -> None:
    plain = Hedron(title="p", security="standard", explorer="off", session_secret="test-secret-ok")

    @plain.page("/")
    def home() -> Page:
        return Page(Text("plain"), title="Home")

    other = Hedron(title="w", security="standard", explorer="off", session_secret="test-secret-ok")

    @other.page("/")
    def home2() -> Page:
        return Page(Text("plain"), title="Home")

    wrapped = workbenchify(other, mode="off")
    a = TestClient(plain).get("/").text
    b = TestClient(wrapped).get("/").text
    assert "plain" in a and "plain" in b


def test_fragment_and_assets_and_openapi() -> None:
    app, region = _app()
    client = TestClient(_RootPathInjector(app, "/s/demo/p/9"))
    home = client.get("/s/demo/p/9/")
    assert home.status_code == 200
    token = home.cookies.get("hedron_csrf")
    assert token
    frag = client.get(
        "/s/demo/p/9/status",
        headers={
            "HX-Request": "true",
            "HX-Target": f"#{region.id}",
            "X-CSRF-Token": token,
        },
    )
    assert frag.status_code == 200
    assert "ok" in frag.text
    assets = client.get("/s/demo/p/9/hedron-static/hedron-default.css")
    assert assets.status_code == 200
    docs = client.get("/s/demo/p/9/docs")
    assert docs.status_code == 200
    spec = client.get("/s/demo/p/9/openapi.json")
    assert spec.status_code == 200


def test_csrf_post_under_constructor_mount() -> None:
    app, _ = _app()
    client = TestClient(_RootPathInjector(app, "/s/demo/p/9"))
    seeded = client.get("/s/demo/p/9/")
    token = seeded.cookies.get("hedron_csrf")
    assert token
    posted = client.post("/s/demo/p/9/ping", headers={"X-CSRF-Token": token})
    assert posted.status_code == 200
    assert "pong" in posted.text


def test_untrusted_connect_header_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HEDRON_ROOT_PATH", raising=False)
    from hedron.mount import resolve_mount_path

    mount = resolve_mount_path(
        root_path=None,
        headers={"rstudio-connect-app-base-url": "https://evil.example/app"},
        peer="10.0.0.9",
        trusted_peers=["127.0.0.1"],
        prefer_env=False,
    )
    assert mount.path == ""


def _connect_request(
    base: str = "https://connect.example/content/abc123",
    *,
    root_path: str = "/content/abc123",
    peer: str = "127.0.0.1",
    duplicate_header: bool = False,
) -> Request:
    headers = [(b"rstudio-connect-app-base-url", base.encode())]
    if duplicate_header:
        headers.append((b"rstudio-connect-app-base-url", base.encode()))
    return Request(
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": f"{root_path}/invite",
            "raw_path": f"{root_path}/invite".encode(),
            "root_path": root_path,
            "query_string": b"",
            "headers": headers,
            "client": (peer, 43120),
            "server": ("127.0.0.1", 8000),
        }
    )


def test_connect_external_base_requires_protected_runtime_evidence() -> None:
    base = connect_external_base_from_request(
        _connect_request(peer="203.0.113.8"), environ={"POSIT_PRODUCT": "CONNECT"}
    )
    assert base is not None
    assert base.origin == "https://connect.example"
    assert base.mount == "/content/abc123"
    assert base.source == "header:rstudio-connect-app-base-url"


@pytest.mark.parametrize(
    ("candidate_request", "message"),
    [
        (_connect_request(peer="10.0.0.8"), "protected runtime evidence"),
        (_connect_request(root_path="/content/other"), "does not match"),
        (_connect_request(base="https://user:pass@connect.example/content/abc123"), "credentials"),
        (_connect_request(base="https://evil.example/content/%2e%2e/admin"), "unsafe mount"),
        (_connect_request(duplicate_header=True), "multiple Posit Connect"),
    ],
)
def test_connect_external_base_rejects_spoofed_or_unsafe_headers(
    candidate_request: Request,
    message: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("POSIT_PRODUCT", raising=False)
    with pytest.raises(ValueError, match=message):
        connect_external_base_from_request(candidate_request, trusted_peers=("127.0.0.1",))


def test_connect_runtime_marker_accepts_forwarded_original_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("POSIT_PRODUCT", "CONNECT")
    base = connect_external_base_from_request(_connect_request(peer="203.0.113.8"))
    assert base is not None
    assert base.origin == "https://connect.example"


def test_external_url_uses_connect_base_and_encodes_invite_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("POSIT_PRODUCT", "CONNECT")
    app = HedronPosit(
        title="connect-url",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
    )
    url = app.external_url(
        "/invites/accept",
        request=_connect_request(),
        query={"token": "one + two", "role": ["reader", "reviewer"]},
    )
    parsed = urlsplit(url)
    assert f"{parsed.scheme}://{parsed.netloc}{parsed.path}" == (
        "https://connect.example/content/abc123/invites/accept"
    )
    assert parse_qs(parsed.query) == {
        "token": ["one + two"],
        "role": ["reader", "reviewer"],
    }
    assert app.hedron_workbench.active is False


def test_external_url_explicit_base_works_outside_workbench() -> None:
    app = HedronPosit(
        title="ordinary-url",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
        external_base_url="https://apps.example/hedron",
    )

    @app.page("/invites/{invite_id}", name="accept_invite")
    def accept_invite(invite_id: str) -> Page:
        return Page(Text(invite_id), title="Invite")

    assert app.external_url_for("accept_invite", invite_id="abc") == (
        "https://apps.example/hedron/invites/abc"
    )
    assert TestClient(app).get("/invites/abc").status_code == 200
    assert app.hedron_workbench.active is False


def test_external_url_uses_active_workbench_resolution_once() -> None:
    app = HedronPosit(
        title="workbench-url",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
        workbench_mount="/s/session/p/8000",
        workbench_public_base_url="https://wb.example/s/session/p/8000",
    )
    assert app.browser_url("/accept") == "https://wb.example/s/session/p/8000/accept"
    assert app.browser_url("/s/session/p/8000/accept") == (
        "https://wb.example/s/session/p/8000/accept"
    )
    with pytest.raises(ValueError, match="session URLs are ephemeral"):
        app.external_url("/accept")
    capabilities = app.deployment_capabilities()
    assert capabilities.browser_links is True
    assert capabilities.durable_links is False
    assert capabilities.ephemeral_session is True


def test_stable_external_base_enables_durable_background_links() -> None:
    app = HedronPosit(
        title="durable",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
        external_base_url="https://apps.example/stable",
    )
    captured = app.external_base()
    assert captured.url == "https://apps.example/stable"
    assert app.external_url("/accept") == "https://apps.example/stable/accept"
    assert app.deployment_capabilities().background_links is True


def test_external_url_rejects_implicit_workbench_loopback_origin() -> None:
    app = HedronPosit(
        title="workbench-loopback",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
        workbench_mount="/s/session/p/8000",
    )
    with pytest.raises(ValueError, match="resolved only a loopback origin"):
        app.external_url("/accept")


def test_explicit_activation_of_constructed_inactive_facade_fails_loudly() -> None:
    app = HedronPosit(
        title="inactive",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
    )
    with pytest.raises(ValueError, match="already-constructed inactive"):
        workbenchify(app, mode="on")


def test_external_url_fails_closed_without_trusted_deployment_base(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = HedronPosit(
        title="no-public-base",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
    )
    with pytest.raises(ValueError, match="no trusted public base URL"):
        app.external_url("/invite")
    monkeypatch.setenv("POSIT_PRODUCT", "CONNECT")
    with pytest.raises(ValueError, match="local absolute path"):
        app.external_url("https://evil.example", request=_connect_request())
    with pytest.raises(ValueError, match="query/fragment"):
        app.external_url("/invite?next=https://evil.example", request=_connect_request())


@pytest.mark.parametrize(
    "base",
    [
        "javascript://example/app",
        "https://user:password@example.test/app",
        "https://example.test/app?token=secret",
        "https://example.test/app#fragment",
        "https://example.test/content/%252e%252e/admin",
        "https://example.test:99999/app",
    ],
)
def test_external_base_url_configuration_rejects_unsafe_values(base: str) -> None:
    with pytest.raises(ValueError):
        HedronPosit(
            title="bad-base",
            security="standard",
            explorer="off",
            session_secret="test-secret-ok",
            external_base_url=base,
        )
