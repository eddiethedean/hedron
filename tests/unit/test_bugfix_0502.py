"""0.50.2 patch: confirmed code defects."""

from __future__ import annotations

import inspect
import io
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from tests.unit._helpers_050 import csrf_headers, make_app, reset_050

from hedron.auth.oidc import OidcClientConfig, login_url, logout_url, validate_callback_state
from hedron.content import process_image
from hedron.handles import _merge_headers, _merge_interaction_policies
from hedron.routing.router import HedronRouter
from hedron.security.login_csrf import issue_login_csrf, validate_login_csrf
from hedron_core.addressable import addressable
from hedron_core.diagnostics import HedronError
from hedron_core.htmx.policy import InteractionPolicy
from hedron_core.interaction import FragmentRegion, InteractionResult, status_policy_for
from hedron_core.plugin_loader import load_plugins
from hedron_core.plugins import PluginMeta
from hedron_core.redis_cache import RedisCacheBackend
from hedron_core.registry import reset_registry_for_tests
from hedron_core.updates import (
    BaseHandleDescriptor,
    PortableTarget,
    RefreshIntent,
    compile_to_interaction,
    refresh_event_name,
    register_handle_descriptor,
    safe_dom_id,
)
from hedron_explorer.services.simulation import parse_regions


def setup_function() -> None:
    reset_050()


def test_login_csrf_length_mismatch_is_403_not_500() -> None:
    session = {"hedron_login_csrf": "a" * 32}
    with pytest.raises(HTTPException) as exc:
        validate_login_csrf("short", session=session)
    assert exc.value.status_code == 403


def test_login_csrf_matching_token_still_succeeds() -> None:
    session: dict[str, str] = {}
    token = issue_login_csrf(session)
    validate_login_csrf(token, session=session)


def test_oidc_state_length_mismatch_is_value_error() -> None:
    with pytest.raises(ValueError, match="state mismatch"):
        validate_callback_state(expected="abcd", received="xy")


def test_oidc_extra_params_cannot_override_protocol_fields() -> None:
    config = OidcClientConfig(
        issuer="https://idp.example",
        client_id="client",
        redirect_uri="https://app.example/callback",
    )
    with pytest.raises(ValueError, match="protocol field"):
        login_url(config, state="st", extra_params={"redirect_uri": "https://evil.example"})


def test_oidc_logout_rejects_javascript_and_foreign_host() -> None:
    config = OidcClientConfig(
        issuer="https://idp.example",
        client_id="client",
        redirect_uri="https://app.example/callback",
        end_session_url="https://idp.example/logout",
    )
    with pytest.raises(ValueError, match="Invalid post_logout_redirect_uri"):
        logout_url(config, post_logout_redirect_uri="javascript:alert(1)")
    with pytest.raises(ValueError, match="host must match"):
        logout_url(config, post_logout_redirect_uri="https://evil.example/")
    url = logout_url(config, post_logout_redirect_uri="https://app.example/bye")
    assert "post_logout_redirect_uri=" in url


def test_empty_app_id_is_foreign_when_expected() -> None:
    target = PortableTarget(
        logical_id="status",
        dom_id="h-view-status",
        path="/status",
        app_id="",
        region=FragmentRegion(id="h-view-status", selector="#h-view-status"),
    )
    with pytest.raises(HedronError, match="HED-UPDATE-0003"):
        compile_to_interaction(RefreshIntent(targets=(target,)), expected_app_id="app-a")


def test_interaction_result_refresh_is_rechecked() -> None:
    reset_registry_for_tests()
    register_handle_descriptor(
        BaseHandleDescriptor(app_id="app-b", logical_id="status", path="/status")
    )
    event = refresh_event_name(safe_dom_id("status"))
    forged = InteractionResult(content=None, trigger={event: {}})
    with pytest.raises(HedronError, match="HED-UPDATE-0003"):
        compile_to_interaction(forged, expected_app_id="app-a")


def test_unregistered_refresh_event_is_foreign() -> None:
    reset_registry_for_tests()
    forged = InteractionResult(content=None, trigger={"hedron:refresh-h-view-ghost": {}})
    with pytest.raises(HedronError, match="HED-UPDATE-0003"):
        compile_to_interaction(forged, expected_app_id="app-a")


def test_ownership_passes_matching_app_id() -> None:
    target = PortableTarget(
        logical_id="status",
        dom_id="h-view-status",
        path="/status",
        app_id="app-a",
        region=FragmentRegion(id="h-view-status", selector="#h-view-status"),
    )
    compiled = compile_to_interaction(RefreshIntent(targets=(target,)), expected_app_id="app-a")
    assert isinstance(compiled, InteractionResult)
    assert compiled.trigger == {refresh_event_name("h-view-status"): {}}
    assert compiled.policy is not None
    assert any(region.id == "h-view-status" for region in compiled.policy.declared_regions)
    with pytest.raises(HedronError, match="HED-UPDATE-0003"):
        compile_to_interaction(RefreshIntent(targets=(target,)), expected_app_id="app-b")


def test_include_component_rolls_back_starlette_route() -> None:
    reset_registry_for_tests()

    @addressable
    def piece() -> str:
        return "ok"

    router = HedronRouter()
    router.include_component(piece, path="/a")
    assert len(router.routes) == 1
    with pytest.raises(HedronError, match="HED-ROUTE-0001"):
        router.include_component(piece, path="/b")
    assert len(router.routes) == 1


def test_action_handle_merges_headers_and_intersects_undeclared_policy() -> None:
    merged = _merge_headers({"HX-A": "1"}, {"HX-B": "2", "HX-A": "old"})
    assert merged == {"HX-B": "2", "HX-A": "1"}
    policy = _merge_interaction_policies(
        InteractionPolicy(allow_undeclared_targets=False),
        InteractionPolicy(allow_undeclared_targets=True),
    )
    assert policy is not None
    assert policy.allow_undeclared_targets is False


def test_fragment_handle_does_not_swallow_hedron_error() -> None:
    from hedron.handles import FragmentHandle

    source = inspect.getsource(FragmentHandle.__call__)
    assert "except Exception" not in source
    assert "ValidationError" in source


def test_status_422_retargets_errors_chrome() -> None:
    policy = status_policy_for(422)
    assert policy.retarget == "#hedron-errors"


def test_htmx_validation_handler_does_not_allow_undeclared_targets() -> None:
    from hedron.responses.handlers import install_interaction_handlers

    source = inspect.getsource(install_interaction_handlers)
    assert "allow_undeclared_targets=False" in source
    assert "allow_undeclared_targets=True" not in source


def test_missing_hx_target_on_handle_host_is_403() -> None:
    app = make_app(security="standard")

    @app.refreshable("/status")
    def status() -> object:
        from hedron_core.builtins.content import Text

        return Text("ok")

    with TestClient(app) as client:
        response = client.get("/status", headers={"HX-Request": "true"})
        assert response.status_code == 403


def test_explorer_simulate_empty_regions_reject_target() -> None:
    regions = parse_regions({})
    target = "#evil"
    region_ok = True
    if target:
        if not regions:
            region_ok = False
        else:
            region_ok = any(target == value.split("|", 1)[0] for _rid, value in regions.items())
    assert region_ok is False

    app = make_app(security="standard", explorer="development")

    @app.page("/")
    def home() -> object:
        from hedron import Page, Text

        return Page(Text("hi"), title="T")

    with TestClient(app) as client:
        body = client.post(
            "/hedron-explorer/api/simulate",
            json={"route": "home", "target": "#evil"},
            headers=csrf_headers(client),
        )
        assert body.status_code == 200
        payload = body.json()
        assert payload["ok"] is False


def test_process_image_requires_root_for_paths(tmp_path: Path) -> None:
    with pytest.raises(HedronError, match="HED-CONTENT-0006"):
        process_image(str(tmp_path / "photo.png"))


def test_process_image_jails_to_root(tmp_path: Path) -> None:
    from PIL import Image

    inside = tmp_path / "ok.png"
    Image.new("RGB", (8, 8), color="red").save(inside)
    outside = tmp_path.parent / "escape.png"
    Image.new("RGB", (8, 8), color="blue").save(outside)
    encoded = process_image(inside, root=tmp_path, max_width=8)
    assert encoded[:8] == b"\x89PNG\r\n\x1a\n"
    with pytest.raises(HedronError, match="HED-CONTENT-0007"):
        process_image(outside, root=tmp_path)


def test_process_image_accepts_bytes() -> None:
    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (8, 8), color="green").save(buf, format="PNG")
    encoded = process_image(buf.getvalue(), max_width=8)
    assert encoded[:8] == b"\x89PNG\r\n\x1a\n"


def test_redis_cache_requires_pipeline() -> None:
    class _NoPipe:
        def get(self, key: str) -> None:
            del key
            return

    backend = RedisCacheBackend(_NoPipe())
    with pytest.raises(ValueError, match="pipeline"):
        backend.set("k", {"v": 1})


def test_invalid_plugin_specifier_is_plugin_failed() -> None:
    reset_registry_for_tests()

    def broken(_ctx: object) -> None:
        return None

    broken.PLUGIN_META = PluginMeta(  # type: ignore[attr-defined]
        name="broken",
        version="0.1.0",
        distribution="broken",
        hedron_version="not-a-spec",
    )

    class EP:
        name = "broken"

        def load(self) -> object:
            return broken

    with pytest.raises(HedronError, match="HED-PLUGIN-0005"):
        load_plugins(entry_points=[EP()], hedron_version="0.50.3")


def test_flask_logged_out_does_not_trust_leftover_session(monkeypatch: pytest.MonkeyPatch) -> None:
    import types

    from flask import session

    from hedron_flask import HedronFlask

    class _User:
        is_authenticated = False

        def get_id(self) -> None:
            return None

    fake = types.ModuleType("flask_login")
    fake.current_user = _User()  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "flask_login", fake)

    hedron = HedronFlask(__name__)
    app = hedron.flask
    assert app is not None
    app.secret_key = "test"
    with app.test_request_context("/"):
        session["user_id"] = "leftover"
        signal = hedron.auth_signal()
    assert signal.authenticated is False


def test_flask_csrf_protect_false_cannot_disable_enabled_policy() -> None:
    from hedron_flask import HedronFlask

    hedron = HedronFlask(__name__, security="standard", csrf_protect=False)
    assert hedron.csrf_protect is True
    assert hedron.security_policy.csrf_enabled is True

    @hedron.page("/", methods=["POST"])
    def home() -> object:
        from hedron import Page, Text

        return Page(Text("ok"), title="home")

    client = hedron.flask.test_client()
    response = client.post("/")
    assert response.status_code == 403


def test_flask_csrf_none_strategy_fails_closed() -> None:
    from hedron_core.security_policy import SecurityPolicy
    from hedron_flask.csrf import assert_flask_csrf_strategy

    policy = SecurityPolicy.from_name("standard")
    with (
        patch.object(SecurityPolicy, "resolve_csrf_strategy", return_value=None),
        pytest.raises(ValueError, match="no CSRF strategy"),
    ):
        assert_flask_csrf_strategy(policy)


def test_flask_auth_signal_error_forces_private_cache() -> None:
    from hedron import Page, Text
    from hedron_flask import HedronFlask

    hedron = HedronFlask(__name__)

    def _boom(_request: object = None) -> object:
        raise RuntimeError("auth failed")

    hedron.auth_signal = _boom  # type: ignore[method-assign]
    assert hedron.flask is not None

    @hedron.page("/")
    def home() -> object:
        return Page(Text("ok"), title="home")

    response = hedron.flask.test_client().get("/")
    assert response.status_code == 200
    cache = response.headers.get("Cache-Control") or ""
    assert "private" in cache
    assert "no-store" in cache
