"""Docs demos authored with ordinary Hedron components + hedron-sim."""

from __future__ import annotations

from hedron import Page, RefreshButton, html, swap
from hedron_sim import SimApp, embed_demo, sim_utc, wrap_browser_chrome

__all__ = ["build_hello_refresh_demo", "hello_refresh_app"]


def hello_refresh_app(*, status_id: str = "service-status") -> SimApp:
    """Scaffold-shaped Hello / Refresh status demo."""
    app = SimApp(title="Hello from hedron new", demo_id=f"hello-refresh-{status_id}")
    status = app.region(status_id, description="Live status panel")

    def status_panel():
        return html.div(
            html.span("✓", class_="hedron-browser-sim__status-icon", aria={"hidden": "true"}),
            html.span(
                f"All systems operational · refreshed {sim_utc()}",
                data={"hbs-stamp": "true"},
            ),
            id=status.id,
            class_="hedron-browser-sim__status",
            role="status",
            aria={"live": "polite"},
        )

    @app.page("/")
    def home() -> Page:
        return Page(
            html.h2("Hello from hedron new", class_="hedron-browser-sim__heading"),
            status_panel(),
            html.div(
                RefreshButton.for_region(
                    status,
                    href="/status",
                    label="Refresh status",
                ),
                html.span(
                    html.span(
                        "→",
                        class_="hedron-browser-sim__hint-arrow",
                        aria={"hidden": "true"},
                    ),
                    " Click — timestamp updates",
                    class_="hedron-browser-sim__hint",
                ),
                class_="hedron-browser-sim__actions",
            ),
            title="Home",
        )

    @app.fragment("/status", region=status)
    def refresh_status():
        return swap(status_panel())

    return app


def build_hello_refresh_demo(
    *,
    status_id: str = "service-status",
    logo_src: str = "assets/hedron-mark.svg",
    caption: str | None = None,
) -> str:
    """HTML island wrapped in docs browser chrome."""
    app = hello_refresh_app(status_id=status_id)
    island = embed_demo(app, class_="hedron-sim hedron-sim--browser", trace=True)
    return wrap_browser_chrome(
        island,
        url="127.0.0.1:8000",
        logo_src=logo_src,
        caption=caption
        or (
            "Docs simulation of <code>127.0.0.1:8000</code> — click "
            "<strong>Refresh status</strong> for an HTMX-style fragment swap (no server)."
        ),
    )
