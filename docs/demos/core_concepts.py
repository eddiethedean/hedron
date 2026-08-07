"""Core-concepts PAGE / FRAGMENT mode toggle for docs."""

from __future__ import annotations

import html as html_lib

from hedron import Page, html
from hedron_core.rendering import RenderMode
from hedron_sim import render_handler_html, sim_utc

__all__ = ["build_core_concepts_modes_demo"]


def build_core_concepts_modes_demo() -> str:
    """Show real PAGE vs FRAGMENT render output side by side (toggle UI)."""
    page = Page(
        html.div("All systems operational", id="service-status"),
        title="Status",
    )
    fragment = html.div(
        f"All systems operational · refreshed {sim_utc()}",
        id="service-status",
        role="status",
    )
    page_html = render_handler_html(page, mode=RenderMode.PAGE)
    frag_html = render_handler_html(fragment, mode=RenderMode.FRAGMENT)

    def pane(mode: str, source: str, *, hidden: bool = False) -> str:
        escaped = html_lib.escape(source)
        hidden_attr = " hidden" if hidden else ""
        return (
            f'<div data-sim-mode-pane="{mode}"{hidden_attr}><pre><code>{escaped}</code></pre></div>'
        )

    return (
        '<section class="hedron-sim hedron-sim--modes" data-hedron-sim-modes="core-concepts">'
        '<div class="hedron-sim__stage">'
        '<div class="hedron-sim-row" role="group" aria-label="Render mode">'
        '<button class="hedron-sim-btn hedron-sim-btn--primary" type="button" '
        'data-sim-mode="page" aria-pressed="true">PAGE</button>'
        '<button class="hedron-sim-btn" type="button" '
        'data-sim-mode="fragment" aria-pressed="false">FRAGMENT</button>'
        "</div>"
        '<div class="hedron-sim-mode-panes">'
        f"{pane('page', page_html)}"
        f"{pane('fragment', frag_html, hidden=True)}"
        "</div>"
        '<p class="hedron-sim-muted" role="status" data-sim-mode-status>'
        "PAGE: full HTML document."
        "</p>"
        "</div>"
        "</section>"
    )
