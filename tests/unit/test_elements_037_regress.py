"""REGRESS-037: high-severity remediations #230–#237."""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any
from unittest.mock import MagicMock

import pytest
from flask import Flask

from hedron_core.builtins.forms_extra import SelectSlider, validate_directory_upload
from hedron_core.diagnostics import HedronError
from hedron_core.htmx_eval import canonical_hx_attribute, hx_attribute_is_url
from hedron_core.jobs import JobState, RedisJobBackend
from hedron_core.rendering import render
from hedron_core.security_policy import SecurityPolicy
from hedron_elements.markup import render_element_markup
from hedron_flask.blueprint import attach_hedron_to_flask
from hedron_mcp.bounds import BoundsError
from hedron_mcp.transport import _origin_forbidden, _read_body_bounded


def test_230_data_hx_canonical_parity() -> None:
    assert canonical_hx_attribute("data-hx-post") == "hx-post"
    assert hx_attribute_is_url("data-hx-post") is True
    assert hx_attribute_is_url("data-hx-target") is False


def test_231_flask_session_cookie_defaults_on_attach() -> None:
    app = Flask(__name__)
    ext = MagicMock()
    ext.auth_signal = None
    ext.security_policy = SecurityPolicy.from_name("strict")
    attach_hedron_to_flask(app, ext, auto_csrf_cookie=False)
    assert app.config["SESSION_COOKIE_SECURE"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"


def test_232_mcp_origin_fail_closed_without_allowlist() -> None:
    class _Req:
        def __init__(self) -> None:
            self.headers = {"origin": "https://evil.example"}

    class _Proj:
        allowed_origins = None

    assert _origin_forbidden(_Req(), _Proj()) is True


def test_232_mcp_origin_allowed_when_absent() -> None:
    class _Req:
        def __init__(self) -> None:
            self.headers: dict[str, str] = {}

    class _Proj:
        allowed_origins = None

    assert _origin_forbidden(_Req(), _Proj()) is False


def test_233_mcp_bounded_body_read() -> None:
    class _Req:
        async def stream(self):
            yield b"x" * 100
            yield b"y" * 100

    with pytest.raises(BoundsError, match="max_request_bytes"):
        asyncio.run(_read_body_bounded(_Req(), max_bytes=150))


def test_234_directory_upload_nul_rejected() -> None:
    with pytest.raises(ValueError, match="Unsafe directory upload path"):
        validate_directory_upload([("a\x00b.txt", 1)], max_files=10, max_total_size=100)


def test_235_select_slider_hidden_value_not_index() -> None:
    html = render(SelectSlider("size", [("s", "S"), ("m", "M"), ("l", "L")], value="l")).html
    match = re.search(r'type="hidden"[^>]*value="([^"]*)"', html)
    assert match is not None
    assert match.group(1) == "l"


def test_236_redis_idempotency_release_uses_eval() -> None:
    from tests.ops.test_redis_jobs import _SharedPipeline, _SharedRedis

    class _EvalRedis(_SharedRedis):
        def __init__(self) -> None:
            super().__init__()
            self.eval_calls: list[tuple[str, str, str]] = []

        def eval(self, script: str, numkeys: int, key: str, expected: str) -> int:
            self.eval_calls.append((script, key, expected))
            if self._store.get(key) == expected:
                self.delete(key)
                return 1
            return 0

        def pipeline(self) -> _SharedPipeline:
            return _SharedPipeline(self)

    shared: Any = _EvalRedis()
    backend = RedisJobBackend(shared)
    handle = backend.submit("demo", {}, idempotency_key="k1", tenant_id="t")
    backend.mark(handle.job_id, JobState.SUCCEEDED)
    raw = shared._store[f"h1:job:{handle.job_id}"]
    data = json.loads(raw)
    idem_key = f"h1:job:idem:{data['idempotency_scope_key']}"
    shared._store[idem_key] = handle.job_id
    data["updated_at"] = 1.0
    shared._store[f"h1:job:{handle.job_id}"] = json.dumps(data)
    assert backend.cleanup_expired(older_than_seconds=10) == 1
    assert shared.eval_calls
    assert shared.get(idem_key) is None


def test_237_markup_rejects_hx_on_attribute() -> None:
    with pytest.raises(HedronError) as exc:
        render_element_markup(
            tag_name="hedron-example",
            abi_version=1,
            element_id="hedron-example",
            attributes={"onclick": "alert(1)"},
            server_content="ok",
        )
    assert exc.value.diagnostic.code == "HED-SEC-0002"


def test_237_markup_rejects_javascript_scheme() -> None:
    with pytest.raises(HedronError) as exc:
        render_element_markup(
            tag_name="hedron-example",
            abi_version=1,
            element_id="hedron-example",
            attributes={"href": "javascript:alert(1)"},
            server_content="ok",
        )
    assert exc.value.diagnostic.code == "HED-SEC-0003"


def test_244_markup_rejects_style_javascript_url() -> None:
    with pytest.raises(HedronError) as exc:
        render_element_markup(
            tag_name="hedron-example",
            abi_version=1,
            element_id="hedron-example",
            attributes={"style": "background:url(javascript:alert(1))"},
            server_content="ok",
        )
    assert exc.value.diagnostic.code == "HED-SEC-0007"


def test_244_markup_rejects_vbscript_and_data_urls() -> None:
    for attributes in (
        {"href": "vbscript:msgbox(1)"},
        {"src": "data:text/html,alert(1)"},
        {"formaction": "vbscript:msgbox(1)"},
    ):
        with pytest.raises(HedronError) as exc:
            render_element_markup(
                tag_name="hedron-example",
                abi_version=1,
                element_id="hedron-example",
                attributes=attributes,
                server_content="ok",
            )
        assert exc.value.diagnostic.code == "HED-SEC-0003"
