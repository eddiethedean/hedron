"""Application runtime isolation contract."""

from __future__ import annotations

from hedron import Hedron, Page, Text
from hedron_core.registry import get_registry, reset_registry_for_tests


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
