"""Optional FastAPI factory and core-only metadata for UI-testing examples."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from hedron_core import Page, RenderMode, render
from hedron_core.html import html
from hedron_sample_kit.components.Callout import Callout

CONTRIBUTION: dict[str, object] = {
    "schema_version": 1,
    "package_id": "hedron-sample-kit",
    "package_version": "0.2.6",
    "hedron_version_range": ">=1.3,<2",
    "capabilities": ["sample_component_app"],
    "fixture_resources": ["sample_kit_app_factory"],
}


def create_app(config: dict[str, object]) -> FastAPI:
    """Build a synthetic app from core and FastAPI without importing Hedron."""
    message = config.get("message", "Sample kit UI-testing contribution")
    if not isinstance(message, str) or not message or len(message) > 120:
        raise ValueError("message must be a non-empty string of at most 120 characters")

    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    def sample_kit_page() -> HTMLResponse:
        page = Page(
            html.main(
                html.h1("Sample kit contribution"),
                html.section(
                    Callout(message=message),
                    id="sample-kit-region",
                    data={"testid": "sample-kit-region"},
                ),
            ),
            title="Sample kit contribution",
        )
        return HTMLResponse(render(page, mode=RenderMode.PAGE).html)

    return app


__all__ = ["CONTRIBUTION", "create_app"]
