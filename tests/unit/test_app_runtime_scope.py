"""Application runtime isolation contract."""

from __future__ import annotations

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from hedron import Hedron, Page, Text
from hedron_core.bundles import FeatureBundle, include_bundle, included_bundles
from hedron_core.cache import get_cache_traces, record_cache_trace
from hedron_core.cache.types import CacheEvent
from hedron_core.compile_gate import assert_runtime_compile_allowed
from hedron_core.component import Component
from hedron_core.diagnostics import HedronError
from hedron_core.models import Props
from hedron_core.registry import get_registry, reset_registry_for_tests
from hedron_core.updates import (
    BaseHandleDescriptor,
    list_handle_descriptors,
    register_handle_descriptor,
)


def test_two_hedron_apps_keep_route_registries_isolated() -> None:
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    first = Hedron(title="first", explorer="off", session_secret="first-secret")
    second = Hedron(title="second", explorer="off", session_secret="second-secret")

    @first.page("/first")
    def first_page() -> Page:
        return Page(Text("first"), title="First")

    @second.page("/second")
    def second_page() -> Page:
        return Page(Text("second"), title="Second")

    with first._hedron_runtime.activate():
        first_routes = {route.path for route in get_registry().routes()}
    with second._hedron_runtime.activate():
        second_routes = {route.path for route in get_registry().routes()}

    assert "/first" in first_routes
    assert "/second" not in first_routes
    assert "/second" in second_routes
    assert "/first" not in second_routes


def test_two_hedron_apps_keep_cache_telemetry_isolated() -> None:
    first = Hedron(title="first-cache", explorer="off", session_secret="first-cache-secret")
    second = Hedron(title="second-cache", explorer="off", session_secret="second-cache-secret")
    event = CacheEvent(kind="miss", key_fingerprint="first", scope="public")

    with first._hedron_runtime.activate():
        record_cache_trace(event)
        assert get_cache_traces() == (event,)
    with second._hedron_runtime.activate():
        assert get_cache_traces() == ()


def test_two_hedron_apps_keep_production_compile_policy_isolated() -> None:
    first = Hedron(title="first-compile", explorer="off", session_secret="first-compile-secret")
    second = Hedron(title="second-compile", explorer="off", session_secret="second-compile-secret")
    first._hedron_runtime.compile_policy.allowed = False
    second._hedron_runtime.compile_policy.allowed = False

    # Stopping one production app restores only that app's policy.
    first._hedron_runtime.compile_policy.allowed = True
    with first._hedron_runtime.activate():
        assert_runtime_compile_allowed()
    with second._hedron_runtime.activate(), pytest.raises(HedronError):
        assert_runtime_compile_allowed()


def test_two_hedron_apps_keep_bundles_and_handles_isolated() -> None:
    first = Hedron(title="first-features", explorer="off", session_secret="first-feature-secret")
    second = Hedron(title="second-features", explorer="off", session_secret="second-feature-secret")
    first_id = first.hedron_app_id
    second_id = second.hedron_app_id

    with first._hedron_runtime.activate():
        include_bundle(
            FeatureBundle(logical_id="tests:first", provider="tests", provider_version="1"),
            app_id=first_id,
        )
        register_handle_descriptor(
            BaseHandleDescriptor(app_id=first_id, logical_id="first", path="/first")
        )
        assert [bundle.logical_id for bundle in included_bundles()] == ["tests:first"]
        assert [handle.logical_id for handle in list_handle_descriptors()] == ["first"]

    with second._hedron_runtime.activate():
        assert included_bundles() == ()
        assert list_handle_descriptors() == ()
        include_bundle(
            FeatureBundle(logical_id="tests:second", provider="tests", provider_version="1"),
            app_id=second_id,
        )

    with first._hedron_runtime.activate():
        assert [bundle.logical_id for bundle in included_bundles()] == ["tests:first"]


def test_public_view_registration_uses_the_owning_handle_registry() -> None:
    first = Hedron(title="first-view", explorer="off", session_secret="first-view-secret")
    second = Hedron(title="second-view", explorer="off", session_secret="second-view-secret")

    @first.view("/status", name="status")
    def first_status() -> Text:
        return Text("first")

    @second.view("/status", name="status")
    def second_status() -> Text:
        return Text("second")

    with first._hedron_runtime.activate():
        assert [item.app_id for item in list_handle_descriptors()] == [first.hedron_app_id]
    with second._hedron_runtime.activate():
        assert [item.app_id for item in list_handle_descriptors()] == [second.hedron_app_id]


def test_router_inclusion_uses_own_runtime_after_another_app_seals() -> None:
    """An app must not consult the compatibility builder owned by another app."""
    first = Hedron(title="first-include", explorer="off", session_secret="first-include-secret")
    second = Hedron(title="second-include", explorer="off", session_secret="second-include-secret")
    router = APIRouter()

    @router.get("/plain")
    def plain() -> dict[str, str]:
        return {"status": "ok"}

    # Sealing the second app changes the process compatibility builder. The
    # first app still has an open builder and must remain able to include a
    # normal FastAPI router.
    with TestClient(second):
        pass
    first.include_router(router)
    assert TestClient(first).get("/plain").json() == {"status": "ok"}


def test_component_inclusion_uses_own_runtime_after_another_app_seals() -> None:
    first = Hedron(title="first-component", explorer="off", session_secret="first-component-secret")
    second = Hedron(
        title="second-component", explorer="off", session_secret="second-component-secret"
    )

    with TestClient(second):
        pass
    first.include_component(lambda: Text("component"), path="/component")
    response = TestClient(first).get("/component")
    assert response.status_code == 200
    assert "component" in response.text


def test_component_prepare_runs_once_per_request() -> None:
    class _Props(Props):
        pass

    class Prepared(Component[_Props]):
        props_type = _Props

        def __init__(self) -> None:
            super().__init__(_Props())
            self.prepare_calls = 0

        async def prepare(self, ctx: object) -> None:
            del ctx
            self.prepare_calls += 1

        def render(self) -> object:
            return Text("prepared")

    app = Hedron(title="prepare-once", explorer="off", session_secret="prepare-secret")
    component = Prepared()

    @app.page("/")
    def home() -> Prepared:
        return component

    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "prepared" in response.text
    assert component.prepare_calls == 1
