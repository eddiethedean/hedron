"""FastAPI TestClient helpers and HTML snapshot utilities."""

from __future__ import annotations

import re
from collections.abc import Generator, Iterator, Mapping, MutableMapping
from contextlib import contextmanager
from typing import Protocol, cast

from hedron.testing.adapters import AdapterAppFixture, AdapterResponse
from hedron_core.registry import get_registry
from hedron_core.rendering import RenderMode, RenderResult, render

__all__ = [
    "as_adapter",
    "assert_non_200_fragment",
    "assert_render_result",
    "assert_renders",
    "fragment_client",
    "iter_named_examples",
    "named_example",
    "normalize_snapshot_html",
    "override_dependencies",
    "render_html",
]


class _HeaderClient(Protocol):
    headers: MutableMapping[str, str]

    def get(self, path: str, *, headers: Mapping[str, str]) -> _TestResponse: ...

    def post(
        self,
        path: str,
        *,
        data: Mapping[str, str],
        headers: Mapping[str, str],
    ) -> _TestResponse: ...


class _CookieItems(Protocol):
    def items(self) -> list[tuple[str, str]]: ...


class _TestResponse(Protocol):
    cookies: _CookieItems
    headers: Mapping[str, str]
    status_code: int
    text: str


def render_html(node: object, *, mode: RenderMode = RenderMode.FRAGMENT) -> str:
    return render(node, mode=mode).html


def assert_renders(node: object, *, contains: str, mode: RenderMode = RenderMode.FRAGMENT) -> str:
    html = render_html(node, mode=mode)
    assert contains in html, f"{contains!r} not found in {html!r}"
    return html


def assert_render_result(result: RenderResult, *, contains: str) -> None:
    assert contains in result.html


def normalize_snapshot_html(html: str) -> str:
    """Normalize only documented nondeterminism (fingerprinted asset hashes)."""
    html = re.sub(r"/hedron-assets/[A-Za-z0-9._-]+", "/hedron-assets/<asset>", html)
    return re.sub(r"\bh-[a-z0-9]{6,}\b", "h-<scoped>", html)


@contextmanager
def override_dependencies(
    app: object,
    overrides: Mapping[object, object],
) -> Generator[None, None, None]:
    """Apply FastAPI ``dependency_overrides`` and restore the prior map on exit."""
    previous = dict(getattr(app, "dependency_overrides", {}))
    app.dependency_overrides.update(dict(overrides))
    try:
        yield
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


def named_example(name: str) -> object | None:
    for meta in get_registry().components():
        if name in meta.examples:
            return {"component": meta.logical_id, "example": name}
    return None


def iter_named_examples() -> Iterator[dict[str, str]]:
    for meta in get_registry().components():
        for example in meta.examples:
            yield {"component": meta.logical_id, "example": example}


def fragment_client(app: object, *, target: str | None = None) -> object:
    """Return a TestClient configured for HTMX fragment requests.

    Pass ``target=`` to set ``HX-Target`` on every request from the client.
    """
    from fastapi.testclient import TestClient

    client = cast(_HeaderClient, TestClient(app))
    client.headers.update({"HX-Request": "true"})
    if target is not None:
        client.headers.update({"HX-Target": target})
    return client


def as_adapter(client: object) -> AdapterAppFixture:
    """Wrap a FastAPI ``TestClient`` (or compatible) as an :class:`AdapterAppFixture`."""
    typed_client = cast(_HeaderClient, client)

    def _cookie_jar(response: object) -> dict[str, str]:
        typed_response = cast(_TestResponse, response)
        jar = {str(key): str(value) for key, value in typed_response.cookies.items()}
        headers = typed_response.headers
        raw = headers.get("Set-Cookie") or headers.get("set-cookie")
        if raw:
            part = str(raw).split(";", 1)[0]
            if "=" in part:
                key, value = part.split("=", 1)
                jar[key.strip()] = value.strip()
        return jar

    def _headers(headers: Mapping[str, str], cookies: Mapping[str, str]) -> dict[str, str]:
        merged = dict(headers)
        if cookies:
            merged["Cookie"] = "; ".join(f"{k}={v}" for k, v in cookies.items())
        return merged

    class _Wrapped:
        name = "fastapi"

        def get(
            self,
            path: str,
            *,
            headers: Mapping[str, str] | None = None,
            cookies: Mapping[str, str] | None = None,
        ) -> AdapterResponse:
            response = typed_client.get(path, headers=_headers(headers or {}, cookies or {}))
            return AdapterResponse(
                response.status_code,
                response.text,
                dict(response.headers),
                _cookie_jar(response),
            )

        def post(
            self,
            path: str,
            *,
            data: Mapping[str, str] | None = None,
            headers: Mapping[str, str] | None = None,
            cookies: Mapping[str, str] | None = None,
        ) -> AdapterResponse:
            response = typed_client.post(
                path,
                data=dict(data or {}),
                headers=_headers(headers or {}, cookies or {}),
            )
            return AdapterResponse(
                response.status_code,
                response.text,
                dict(response.headers),
                _cookie_jar(response),
            )

    return _Wrapped()


def _response_status(response: object) -> int:
    return int(response.status_code)


def _response_body(response: object) -> str:
    body = getattr(response, "body", None)
    if isinstance(body, str):
        return body
    text = getattr(response, "text", None)
    if isinstance(text, str):
        return text
    content = getattr(response, "content", None)
    if isinstance(content, (bytes, bytearray)):
        return bytes(content).decode("utf-8", errors="replace")
    return str(response)


def assert_non_200_fragment(
    response: object,
    *,
    status_code: int,
    contains: str | None = None,
) -> None:
    """Assert a non-200 fragment/error response (validation HTML, region deny, etc.)."""
    actual = _response_status(response)
    assert actual == status_code, f"expected status {status_code}, got {actual}"
    assert actual != 200
    body = _response_body(response)
    assert "<html" not in body.lower(), f"expected fragment/error body without chrome, got {body!r}"
    if contains is not None:
        assert contains in body, f"{contains!r} not found in {body!r}"
