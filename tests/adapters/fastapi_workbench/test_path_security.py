"""Absolute-URL path decoding security for fastapi-workbench (issue #142)."""

from __future__ import annotations

from urllib.parse import quote

import pytest

from fastapi_workbench.config import WorkbenchMode
from fastapi_workbench.middleware import WorkbenchPathMiddleware, _unsafe_decoded_path
from fastapi_workbench.mount import is_local_path


class _NullApp:
    async def __call__(self, scope: object, receive: object, send: object) -> None:
        return None


def test_unsafe_decoded_path_rejects_semicolon_smuggling() -> None:
    assert _unsafe_decoded_path("/..;/secret") is True
    assert _unsafe_decoded_path("/%2e%2e%3b/secret") is True
    assert _unsafe_decoded_path("/..%3b/secret") is True
    assert is_local_path("/..;/etc") is False


def test_unsafe_decoded_path_allows_normal_local_paths() -> None:
    assert _unsafe_decoded_path("/s/session/p/1/login") is False
    assert _unsafe_decoded_path("/") is False


def test_absolute_url_semicolon_smuggling_raises() -> None:
    mw = WorkbenchPathMiddleware(
        _NullApp(),
        mode=WorkbenchMode.ON,
        expected_origins=("https://workbench.example",),
        active=True,
    )
    scope = {
        "type": "http",
        "path": "https%3A//workbench.example/..%3B/secret",
        "root_path": "",
        "query_string": b"",
    }
    with pytest.raises(Exception) as exc:
        mw.normalize_scope(scope)  # type: ignore[arg-type]
    assert getattr(exc.value, "status_code", None) == 400
    assert "unsafe" in str(exc.value).lower() or "path" in str(exc.value).lower()


def test_absolute_url_encoded_dotdot_semicolon_raises() -> None:
    mw = WorkbenchPathMiddleware(
        _NullApp(),
        mode=WorkbenchMode.ON,
        expected_origins=("https://wb.example",),
    )
    target = "/" + quote("https://wb.example/%2e%2e%3b/admin", safe="")
    with pytest.raises(Exception) as exc:
        mw.normalize_scope(
            {
                "type": "http",
                "path": target,
                "root_path": "",
                "query_string": b"",
            }
        )
    assert getattr(exc.value, "status_code", None) == 400


def test_absolute_url_safe_path_still_decodes() -> None:
    mw = WorkbenchPathMiddleware(
        _NullApp(),
        mode=WorkbenchMode.ON,
        expected_origins=("https://workbench.example",),
    )
    encoded = "/" + quote("https://workbench.example/s/session/p/1/login", safe="")
    out = mw.normalize_scope(
        {
            "type": "http",
            "path": encoded,
            "root_path": "",
            "query_string": b"",
        }
    )
    assert out["path"] == "/s/session/p/1/login"
