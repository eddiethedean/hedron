"""Public testing helpers for Hedron applications."""

from __future__ import annotations

import re
from collections.abc import Generator, Iterator, Mapping
from contextlib import contextmanager
from typing import Any

from hedron.testing.adapters import (
    AdapterAppFixture,
    AdapterResponse,
    assert_fragment_body,
    assert_html_contains,
    assert_htmx_trigger,
    assert_hx_push_url,
    assert_hx_redirect,
    assert_hx_reswap,
    assert_hx_retarget,
    assert_oob_present,
    assert_page_document,
    assert_toast_markup,
    assert_lazy_markup,
    assert_pagination_markup,
    assert_tabs_markup,
    assert_dialog_markup,
    django_fixture,
    fastapi_fixture,
    flask_fixture,
)
from hedron.testing.data import (
    AdversarialCase,
    assert_accessible_fallback,
    assert_budget,
    assert_stable_row_identity,
    assert_stable_trace_identity,
    chart_event_fixture,
    data_changes_fixture,
    data_query_fixture,
    grid_event_fixture,
    labeled_adversarial_cases,
    transform_plan_fixture,
)
from hedron_core.registry import get_registry
from hedron_core.rendering import RenderMode, RenderResult, render
from hedron_core.testing.app import (
    AppScenario,
    MarkedElement,
    find_all_marks,
    find_mark,
)
from hedron_core.testing.async_scenario import (
    AsyncScenario,
    ControllableClock,
    ScriptedDependency,
    assert_ordered_events,
    scripted_outcome,
)
from hedron_core.testing.fixtures import (
    AuthPrincipal,
    BrowserHintFixture,
    NamedConnectionFixture,
    OidcCallbackStub,
    StoragePayload,
    UploadFixture,
    redact_secrets_for_failure,
    validate_fixture,
)
from hedron_core.testing.htmx_asserts import (
    assert_shell_dual_path,
    assert_ui_targets_subset_of_regions,
    assert_undeclared_target_rejected,
)
from hedron_core.testing.workbench import (
    SandboxBudgetFixture,
    assert_action_authorized,
    assert_http_fallback_present,
    assert_transform_plan_bounded,
    image_region_fixture,
    json_document_fixture,
    sandbox_budget_fixture,
    tree_document_fixture,
    workbench_action_fixture,
)

__all__ = [
    "AdapterAppFixture",
    "AdapterResponse",
    "AdversarialCase",
    "AppScenario",
    "AsyncScenario",
    "AuthPrincipal",
    "BrowserHintFixture",
    "ControllableClock",
    "MarkedElement",
    "NamedConnectionFixture",
    "OidcCallbackStub",
    "SandboxBudgetFixture",
    "ScriptedDependency",
    "StoragePayload",
    "UploadFixture",
    "as_adapter",
    "assert_accessible_fallback",
    "assert_action_authorized",
    "assert_budget",
    "assert_fragment_body",
    "assert_html_contains",
    "assert_http_fallback_present",
    "assert_htmx_trigger",
    "assert_hx_push_url",
    "assert_hx_redirect",
    "assert_hx_reswap",
    "assert_hx_retarget",
    "assert_non_200_fragment",
    "assert_oob_present",
    "assert_ordered_events",
    "assert_page_document",
    "assert_render_result",
    "assert_renders",
    "assert_shell_dual_path",
    "assert_stable_row_identity",
    "assert_stable_trace_identity",
    "assert_toast_markup",
    "assert_lazy_markup",
    "assert_pagination_markup",
    "assert_tabs_markup",
    "assert_dialog_markup",
    "assert_transform_plan_bounded",
    "assert_ui_targets_subset_of_regions",
    "assert_undeclared_target_rejected",
    "chart_event_fixture",
    "data_changes_fixture",
    "data_query_fixture",
    "django_fixture",
    "fastapi_fixture",
    "find_all_marks",
    "find_mark",
    "flask_fixture",
    "fragment_client",
    "grid_event_fixture",
    "image_region_fixture",
    "iter_named_examples",
    "json_document_fixture",
    "labeled_adversarial_cases",
    "named_example",
    "normalize_snapshot_html",
    "override_dependencies",
    "redact_secrets_for_failure",
    "render_html",
    "sandbox_budget_fixture",
    "scripted_outcome",
    "transform_plan_fixture",
    "tree_document_fixture",
    "validate_fixture",
    "workbench_action_fixture",
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
