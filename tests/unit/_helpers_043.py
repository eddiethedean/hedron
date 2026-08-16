"""Shared helpers for phase 0.43 tests."""

from __future__ import annotations

from collections.abc import Callable

from fastapi.testclient import TestClient

from hedron import Hedron
from hedron_core.registry import reset_registry_for_tests

__all__ = ["csrf_headers", "make_app", "reset_043"]


def reset_043() -> None:
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]


def make_app(*, explorer: str = "off", security: str = "development") -> Hedron:
    reset_043()
    return Hedron(
        title="phase-043",
        security=security,
        explorer=explorer,
        session_secret="secret-for-tests-32chars-ok!!",
    )


def csrf_headers(client: TestClient, *, htmx: bool = True) -> dict[str, str]:
    home = client.get("/")
    token = home.cookies.get("hedron_csrf") or client.cookies.get("hedron_csrf") or ""
    headers = {"X-CSRF-Token": token}
    if htmx:
        headers["HX-Request"] = "true"
    return headers


def with_client(app: Hedron, fn: Callable[[TestClient], None]) -> None:
    with TestClient(app) as client:
        fn(client)
