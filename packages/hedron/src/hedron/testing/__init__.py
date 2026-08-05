"""Public testing helpers for Hedron applications."""

from __future__ import annotations

import re
from collections.abc import Generator, Iterator, Mapping
from contextlib import contextmanager
from typing import Any

from hedron_core.registry import get_registry
from hedron_core.rendering import RenderMode, RenderResult, render

__all__ = [
    "assert_render_result",
    "assert_renders",
    "fragment_client",
    "iter_named_examples",
    "named_example",
    "normalize_snapshot_html",
    "override_dependencies",
    "render_html",
    # Portable adapter harness (0.11)
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


def __getattr__(name: str) -> Any:
    if name in {
        "AdapterAppFixture",
        "AdapterResponse",
        "assert_fragment_body",
        "assert_html_contains",
        "assert_htmx_trigger",
        "assert_page_document",
        "django_fixture",
        "fastapi_fixture",
        "flask_fixture",
    }:
        from hedron.testing import adapters as _adapters

        return getattr(_adapters, name)
    raise AttributeError(name)


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


def fragment_client(app: Any) -> Any:
    """Return a TestClient configured for HTMX fragment requests."""
    from fastapi.testclient import TestClient

    client = TestClient(app)
    client.headers.update({"HX-Request": "true"})
    return client
