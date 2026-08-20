"""Locked 14-issue phase 0.41 regression packet."""

from __future__ import annotations

import asyncio
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from flask import Flask
from pydantic import BaseModel
from starlette.requests import Request

from fastapi_workbench.config import WorkbenchConfig
from fastapi_workbench.resolve import explicit_mount_hint
from hedron.connections import ConnectionRegistry
from hedron.state import SessionState, session_state
from hedron.websocket_channel import accept_page_session_channel
from hedron_core import Text
from hedron_core.adapter import UrlReverseRequest
from hedron_core.builtins.forms import Form, Hx
from hedron_core.builtins.shell import HtmxLink
from hedron_core.channel import PageSessionChannel
from hedron_core.diagnostics import HedronError
from hedron_core.htmx.policy import FragmentRegion, InteractionPolicy, OobUpdate
from hedron_core.htmx_eval import reject_hx_eval_value
from hedron_core.interaction import InteractionResult
from hedron_flask.routing import FlaskUrlReverser

ISSUES = (70, 74, 85, 98, 103, 106, 135, 149, 150, 185, 186, 200, 202, 207)

_R = "tests/unit/test_regress_041_issues.py"
_A = "tests/adapters"
_U = "tests/unit"
ISSUE_TESTS: dict[int, str] = {
    70: f"{_R}::test_issue_70_multi_target_select_oob_accepted",
    74: f"{_U}/test_prerelease_0282_adapter_parity.py::test_fastapi_honors_allow_htmx_eval_policy",
    85: f"{_R}::test_issue_85_duplicate_oob_element_ids_rejected",
    98: f"{_R}::test_issue_98_rejects_non_object_json_frames",
    103: f"{_U}/test_adaptive_concurrency.py::test_issue_103_cancels_siblings_on_overload",
    106: f"{_R}::test_issue_106_connection_registry_single_flight",
    135: (
        f"{_A}/fastapi_workbench/test_resolve.py::"
        "test_issue_135_resolved_public_base_preserves_mount_path"
    ),
    149: f"{_R}::test_issue_149_session_state_refreshes_after_direct_session_mutation",
    150: f"{_R}::test_issue_150_duplicate_session_state_dependencies_share_cache",
    185: f"{_R}::test_explicit_mount_hint_accepts_hedron_root_path",
    186: (
        f"{_A}/fastapi_workbench/test_runner.py::"
        "test_run_target_skips_discovery_when_uvicorn_root_path_set"
    ),
    200: f"{_R}::test_zero_width_unicode_cannot_hide_js_eval",
    202: f"{_R}::test_issue_202_url_reversal_uses_boundary_safe_mount_prefix",
    207: f"{_U}/test_sse.py::test_issue_207",
}


def test_every_locked_issue_has_bound_evidence() -> None:
    root = Path(__file__).resolve().parents[2]
    assert len(ISSUES) == 14
    assert tuple(ISSUE_TESTS) == ISSUES
    for issue, node in ISSUE_TESTS.items():
        path = root / node.split("::", 1)[0]
        assert path.is_file(), f"#{issue} evidence missing file {path}"
        name = node.split("::", 1)[1] if "::" in node else ""
        if name:
            assert f"def {name}(" in path.read_text(encoding="utf-8"), (
                f"#{issue} missing test {name} in {path}"
            )


def test_explicit_mount_hint_accepts_hedron_root_path() -> None:
    assert (
        explicit_mount_hint(WorkbenchConfig(), {"HEDRON_ROOT_PATH": "/s/session/p/1"})
        == "/s/session/p/1"
    )


def test_zero_width_unicode_cannot_hide_js_eval() -> None:
    for value in ("js\u200b:alert(1)", "js\u200c:alert(1)", "js\ufeff:alert(1)"):
        try:
            reject_hx_eval_value("hx-vals", value)
        except HedronError as exc:
            assert "HED-SEC-0011" in str(exc)
        else:
            raise AssertionError(f"eval value accepted: {value!r}")


def test_issue_70_multi_target_select_oob_accepted() -> None:
    """#70: request-side controls accept comma-separated #id select_oob lists."""
    assert Hx(select_oob="#a, #b").as_html_attrs()["hx-select-oob"] == "#a, #b"
    assert HtmxLink("go", "/", select_oob="#a, #b").props.select_oob == "#a, #b"
    Form(Text("x"), action="/save", hx=Hx(select_oob="#toast, #side"))
    with pytest.raises(ValueError, match="simple #id"):
        HtmxLink("go", "/", select_oob="#ok, nav.side")


def test_issue_85_duplicate_oob_element_ids_rejected() -> None:
    """#85: duplicate OobUpdate element_id fails closed at compile and materialize."""
    policy = InteractionPolicy(
        declared_regions=(
            FragmentRegion(id="main", selector="#main"),
            FragmentRegion(id="side", selector="#side"),
        )
    )
    with pytest.raises(ValueError, match="duplicate OobUpdate"):
        InteractionResult(
            content="main",
            region_id="main",
            policy=policy,
            oob=(
                OobUpdate(content="A", element_id="side"),
                OobUpdate(content="B", element_id="side"),
            ),
        )


def test_issue_98_rejects_non_object_json_frames() -> None:
    """#98: valid non-object JSON must not crash the channel handler."""
    channel = PageSessionChannel(
        channel_id="c1",
        declared_regions=frozenset({"status"}),
        declared_client_reads=(),
    )
    websocket = MagicMock()
    websocket.headers = {"origin": "https://example.com"}
    websocket.url = type("U", (), {"hostname": "example.com", "scheme": "wss", "port": None})()
    websocket.accept = AsyncMock()
    websocket.close = AsyncMock()
    websocket.send_text = AsyncMock()

    for payload in ("[]", "null", "true", "1", '"text"'):
        websocket.receive_text = AsyncMock(return_value=payload)

        async def _run() -> None:
            await accept_page_session_channel(websocket, channel)  # type: ignore[arg-type]

        asyncio.run(_run())
        sent = [json.loads(call.args[0]) for call in websocket.send_text.await_args_list]
        assert any(msg.get("detail") == "invalid json message" for msg in sent)
        websocket.send_text.reset_mock()
        websocket.close.reset_mock()


def test_issue_106_connection_registry_single_flight() -> None:
    """#106: concurrent first get creates one instance and returns the same object."""
    registry = ConnectionRegistry()
    calls = 0
    started = threading.Event()
    release = threading.Event()

    def factory() -> object:
        nonlocal calls
        calls += 1
        started.set()
        assert release.wait(timeout=2.0)
        return object()

    registry.register("db", factory)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(registry.get, "db") for _ in range(2)]
        assert started.wait(timeout=2.0)
        assert calls == 1
        release.set()
        values = [future.result(timeout=2.0) for future in futures]
    assert calls == 1
    assert len({id(value) for value in values}) == 1
    assert id(registry.get("db")) == id(values[0])


def test_issue_202_url_reversal_uses_boundary_safe_mount_prefix() -> None:
    """#202: sibling route paths must not skip mount prefixing."""
    app = Flask("rev")

    @app.route("/apple/<item_id>", endpoint="apple")
    def apple(item_id: str) -> str:
        return item_id

    rev = FlaskUrlReverser(app)
    with app.test_request_context("/"):
        mounted = rev.reverse(
            UrlReverseRequest(name="apple", kwargs={"item_id": "1"}, script_name="/app")
        )
    assert mounted == "/app/apple/1"

    from hedron_django.routing import DjangoUrlReverser

    try:
        import django
        from django.conf import settings
        from django.urls import clear_url_caches, set_urlconf

        if not settings.configured:
            settings.configure(
                ROOT_URLCONF="tests.adapters.django.urls",
                SECRET_KEY="test",
                ALLOWED_HOSTS=["*"],
                MIDDLEWARE=[],
                INSTALLED_APPS=["django.contrib.contenttypes"],
            )
            django.setup()
        else:
            set_urlconf("tests.adapters.django.urls")
            clear_url_caches()
    except Exception:  # noqa: BLE001
        pytest.skip("Django not available")

    django_rev = DjangoUrlReverser()
    assert django_rev.reverse(UrlReverseRequest(name="home", root_path="/app")) == "/app/"


class _Settings(BaseModel):
    count: int = 0


def test_issue_149_session_state_refreshes_after_direct_session_mutation() -> None:
    request = Request({"type": "http", "session": {"settings": {"count": 1}}, "headers": []})
    state = SessionState(request, "settings", _Settings)
    state.value.count += 1
    assert state.value.count == 2
    request.session["settings"]["count"] = 99
    assert state.value.count == 99


def test_issue_150_duplicate_session_state_dependencies_share_cache() -> None:
    request = Request({"type": "http", "session": {"settings": {"count": 1}}, "headers": []})
    dep = session_state("settings", _Settings)

    async def _load() -> tuple[SessionState[_Settings], SessionState[_Settings]]:
        return await dep.dependency(request), await dep.dependency(request)

    first, second = asyncio.run(_load())
    assert first is second
    first.value.count += 1
    assert second.value.count == 2
