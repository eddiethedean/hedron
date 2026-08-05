"""Portable adapter test harness (phase 0.11).

Exposes only guarantees shared across FastAPI, Flask, and Django. Host-native
clients and assertions remain available beside these helpers.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

__all__ = [
    "AdapterAppFixture",
    "AdapterResponse",
    "assert_fragment_body",
    "assert_html_contains",
    "assert_htmx_trigger",
    "assert_page_document",
    "django_fixture",
    "fastapi_fixture",
    "flask_fixture",
]


@dataclass(frozen=True, slots=True)
class AdapterResponse:
    status_code: int
    body: str
    headers: Mapping[str, str]


@runtime_checkable
class AdapterAppFixture(Protocol):
    """Common app-fixture protocol for portable scenarios."""

    name: str

    def get(
        self,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
    ) -> AdapterResponse: ...

    def post(
        self,
        path: str,
        *,
        data: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
    ) -> AdapterResponse: ...


def assert_html_contains(response: AdapterResponse, needle: str) -> None:
    assert needle in response.body, f"{needle!r} not found in {response.body!r}"


def assert_page_document(response: AdapterResponse) -> None:
    assert response.status_code == 200
    lower = response.body.lower()
    assert "<html" in lower
    assert "</html>" in lower


def assert_fragment_body(response: AdapterResponse, *, contains: str) -> None:
    assert response.status_code == 200
    assert contains in response.body
    assert "<html" not in response.body.lower()


def assert_htmx_trigger(response: AdapterResponse, event: str) -> None:
    trigger = response.headers.get("HX-Trigger") or response.headers.get("hx-trigger")
    assert trigger is not None and event in trigger


@dataclass
class _ClientFixture:
    name: str
    _get: Callable[..., AdapterResponse]
    _post: Callable[..., AdapterResponse]

    def get(
        self,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
    ) -> AdapterResponse:
        return self._get(path, headers=headers or {}, cookies=cookies or {})

    def post(
        self,
        path: str,
        *,
        data: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
    ) -> AdapterResponse:
        return self._post(path, data=data or {}, headers=headers or {}, cookies=cookies or {})


def fastapi_fixture(app: Any) -> AdapterAppFixture:
    from fastapi.testclient import TestClient

    client = TestClient(app)

    def _headers(headers: Mapping[str, str], cookies: Mapping[str, str]) -> dict[str, str]:
        merged = dict(headers)
        if cookies:
            merged["Cookie"] = "; ".join(f"{k}={v}" for k, v in cookies.items())
        return merged

    def get(path: str, headers: Mapping[str, str], cookies: Mapping[str, str]) -> AdapterResponse:
        response = client.get(path, headers=_headers(headers, cookies))
        return AdapterResponse(response.status_code, response.text, dict(response.headers))

    def post(
        path: str,
        data: Mapping[str, str],
        headers: Mapping[str, str],
        cookies: Mapping[str, str],
    ) -> AdapterResponse:
        response = client.post(path, data=dict(data), headers=_headers(headers, cookies))
        return AdapterResponse(response.status_code, response.text, dict(response.headers))

    return _ClientFixture("fastapi", get, post)


def flask_fixture(app: Any) -> AdapterAppFixture:
    client = app.test_client()

    def get(path: str, headers: Mapping[str, str], cookies: Mapping[str, str]) -> AdapterResponse:
        response = client.get(path, headers=dict(headers))
        for key, value in cookies.items():
            client.set_cookie(key, value)
        body = response.get_data(as_text=True)
        return AdapterResponse(response.status_code, body, dict(response.headers))

    def post(
        path: str,
        data: Mapping[str, str],
        headers: Mapping[str, str],
        cookies: Mapping[str, str],
    ) -> AdapterResponse:
        for key, value in cookies.items():
            client.set_cookie(key, value)
        response = client.post(path, data=dict(data), headers=dict(headers))
        body = response.get_data(as_text=True)
        return AdapterResponse(response.status_code, body, dict(response.headers))

    return _ClientFixture("flask", get, post)


def django_fixture(client: Any) -> AdapterAppFixture:
    """Wrap a Django test client."""

    def get(path: str, headers: Mapping[str, str], cookies: Mapping[str, str]) -> AdapterResponse:
        for key, value in cookies.items():
            client.cookies[key] = value
        response = client.get(path, headers=dict(headers))
        body = response.content.decode("utf-8")
        return AdapterResponse(response.status_code, body, dict(response.headers))

    def post(
        path: str,
        data: Mapping[str, str],
        headers: Mapping[str, str],
        cookies: Mapping[str, str],
    ) -> AdapterResponse:
        for key, value in cookies.items():
            client.cookies[key] = value
        response = client.post(path, data=dict(data), headers=dict(headers))
        body = response.content.decode("utf-8")
        return AdapterResponse(response.status_code, body, dict(response.headers))

    return _ClientFixture("django", get, post)
