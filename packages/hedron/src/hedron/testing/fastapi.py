"""FastAPI TestClient helpers and HTML snapshot utilities."""

from __future__ import annotations

import re
from collections.abc import Generator, Iterator, Mapping
from contextlib import contextmanager
from typing import Any

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


def render_html(node: Any, *, mode: RenderMode = RenderMode.FRAGMENT) -> str:
    return render(node, mode=mode).html


def assert_renders(node: Any, *, contains: str, mode: RenderMode = RenderMode.FRAGMENT) -> str:
    html = render_html(node, mode=mode)
    assert contains in html, f"{contains!r} not found in {html!r}"
    return html


def assert_render_result(result: RenderResult, *, contains: str) -> None:
    assert contains in result.html


def normalize_snapshot_html(html: str) -> str:
    """Normalize only documented nondeterminism (fingerprinted asset hashes)."""
    html = re.sub(r"/hedron-assets/[A-Za-z0-9._-]+", "/hedron-assets/<asset>", html)
    html = re.sub(r"\bh-[a-z0-9]{6,}\b", "h-<scoped>", html)
    return html


@contextmanager
def override_dependencies(
    app: Any,
    overrides: Mapping[Any, Any],
) -> Generator[None, None, None]:
    """Apply FastAPI ``dependency_overrides`` and restore the prior map on exit."""
    previous = dict(getattr(app, "dependency_overrides", {}))
    app.dependency_overrides.update(dict(overrides))
    try:
        yield
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


def named_example(name: str) -> Any | None:
    for meta in get_registry().components():
        if name in meta.examples:
            return {"component": meta.logical_id, "example": name}
    return None


def iter_named_examples() -> Iterator[dict[str, str]]:
    for meta in get_registry().components():
        for example in meta.examples:
            yield {"component": meta.logical_id, "example": example}


def fragment_client(app: Any, *, target: str | None = None) -> Any:
    """Return a TestClient configured for HTMX fragment requests.

    Pass ``target=`` to set ``HX-Target`` on every request from the client.
    """
    from fastapi.testclient import TestClient

    client = TestClient(app)
    client.headers.update({"HX-Request": "true"})
    if target is not None:
        client.headers.update({"HX-Target": target})
    return client


def as_adapter(client: Any) -> AdapterAppFixture:
    """Wrap a FastAPI ``TestClient`` (or compatible) as an :class:`AdapterAppFixture`."""

    def _cookie_jar(response: Any) -> dict[str, str]:
        jar = {str(k): str(v) for k, v in getattr(response, "cookies", {}).items()}
        headers = getattr(response, "headers", {})
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
            response = client.get(path, headers=_headers(headers or {}, cookies or {}))
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
            response = client.post(
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


def _response_status(response: Any) -> int:
    return int(response.status_code)


def _response_body(response: Any) -> str:
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
    response: Any,
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
