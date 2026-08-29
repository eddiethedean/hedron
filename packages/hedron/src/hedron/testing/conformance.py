"""FastAPI adapter conformance skeleton (Flask/Django deferred to 0.7)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol, cast

__all__ = ["fastapi_conformance_checks"]


class _Response(Protocol):
    status_code: int


class _Client(Protocol):
    def get(self, url: str) -> _Response: ...


def fastapi_conformance_checks(app_factory: Callable[[], Any]) -> list[str]:
    """Return human-readable conformance findings for a Hedron FastAPI app."""
    from fastapi.testclient import TestClient

    findings: list[str] = []
    app = app_factory()
    with TestClient(app) as client:
        if (
            any(getattr(r, "path", "").startswith("/hedron-explorer") for r in app.routes)
            and getattr(app, "hedron_explorer_mode", "off") == "off"
        ):
            findings.append("Explorer should be absent when explorer='off'")
        # Smoke GET of OpenAPI
        response = cast(_Client, client).get("/openapi.json")
        if response.status_code >= 500:
            findings.append("OpenAPI document failed to render")
    return findings
