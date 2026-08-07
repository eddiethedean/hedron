"""Render SimApp handlers to HTML islands for static docs."""

from __future__ import annotations

import html as html_lib
import json
from collections.abc import Callable, Mapping
from typing import Any

from hedron_core.builtins import Fragment
from hedron_core.builtins.document import Page
from hedron_core.interaction import InteractionResult, materialize_interaction_nodes
from hedron_core.rendering import RenderMode, render
from hedron_sim.app import SimApp, SimRoute

__all__ = ["embed_demo", "render_handler_html", "route_table", "wrap_browser_chrome"]


def _page_body(page: Page) -> Any:
    """Return the page body tree without the document chrome."""
    raw = getattr(page, "_children", ())
    children: tuple[Any, ...] = tuple(raw) if raw else ()
    if not children:
        return Fragment()
    if len(children) == 1:
        return children[0]
    return Fragment(*children)


def render_handler_html(value: Any, *, mode: RenderMode = RenderMode.FRAGMENT) -> str:
    """Render a page/component/``InteractionResult`` to an HTML string."""
    if isinstance(value, InteractionResult):
        node = materialize_interaction_nodes(value)
        if node is None:
            return ""
        return render(node, mode=RenderMode.FRAGMENT).html
    if isinstance(value, Page):
        if mode is RenderMode.PAGE:
            return render(value, mode=RenderMode.PAGE).html
        return render(_page_body(value), mode=RenderMode.FRAGMENT).html
    if value is None:
        return ""
    return render(value, mode=mode).html  # type: ignore[arg-type]


def _render_call(handler: Callable[..., Any]) -> dict[str, Any]:
    body = handler()
    status = 200
    if isinstance(body, InteractionResult):
        status = int(body.status_code or 200)
    return {"html": render_handler_html(body), "status": status}


def _region_payload(route: SimRoute) -> list[dict[str, str]]:
    return [
        {"id": region.id, "selector": region.selector, "description": region.description}
        for region in route.regions
    ]


def route_table(app: SimApp) -> dict[str, Any]:
    """Build the JSON payload consumed by ``hedron-sim.js``."""
    routes: dict[str, Any] = {}
    for key, route in app.routes.items():
        primary = _render_call(route.handler)
        entry: dict[str, Any] = {
            **primary,
            "regions": _region_payload(route),
            "explanation": route.explanation,
        }
        if route.validate:
            entry["validate"] = route.validate
        if route.variants:
            entry["variants"] = {
                name: _render_call(handler) for name, handler in route.variants.items()
            }
        if route.sequence:
            entry["sequence"] = [_render_call(handler) for handler in route.sequence]
        if route.accumulate:
            if route.empty is not None:
                empty_body = _render_call(route.empty)
            else:
                empty_body = {"html": "", "status": 200}
            entry["accumulate"] = {
                "field": route.accumulate,
                "itemHtml": primary["html"],
                "emptyHtml": empty_body["html"],
            }
        if route.list_remove:
            entry["listRemove"] = True
        routes[key] = entry
    return {
        "demoId": app.demo_id or "hedron-sim",
        "title": app.title,
        "pagePath": app.page_path,
        "routes": routes,
    }


def embed_demo(
    app: SimApp,
    *,
    class_: str = "hedron-sim",
    trace: bool = True,
    attrs: Mapping[str, str] | None = None,
) -> str:
    """Render the page body plus an embedded route table for the JS runtime.

    The returned HTML is safe to paste into MkDocs markdown (with ``md_in_html``).
    """
    if app.page_handler is None:
        raise ValueError("SimApp has no @app.page handler; register one before embed_demo().")

    page_html = render_handler_html(app.page_handler(), mode=RenderMode.FRAGMENT)
    table = route_table(app)
    demo_id = html_lib.escape(app.demo_id or "hedron-sim", quote=True)
    classes = html_lib.escape(class_, quote=True)
    extra = ""
    if attrs:
        parts = [
            f'{html_lib.escape(key, quote=True)}="{html_lib.escape(str(value), quote=True)}"'
            for key, value in attrs.items()
        ]
        extra = " " + " ".join(parts)

    payload = json.dumps(table, ensure_ascii=False, separators=(",", ":"))
    # Escape HTML specials so the payload is safe inside a normal element
    # (Material instant navigation strips <script> nodes from fetched pages).
    payload = payload.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    trace_html = (
        '<p class="hedron-sim__trace" data-hedron-sim-trace aria-live="polite" hidden></p>'
        if trace
        else ""
    )
    return (
        f'<section class="{classes}" data-hedron-sim="{demo_id}"{extra}>'
        f'<div class="hedron-sim__stage" data-hedron-sim-stage>{page_html}</div>'
        f"{trace_html}"
        # <template> survives MkDocs Material instant navigation; <script> does not.
        f"<template data-hedron-sim-routes>{payload}</template>"
        "</section>"
    )


def wrap_browser_chrome(
    inner_html: str,
    *,
    url: str = "127.0.0.1:8000",
    caption: str | None = None,
    logo_src: str | None = None,
) -> str:
    """Optional docs browser chrome around an ``embed_demo`` island or stage HTML."""
    logo = ""
    if logo_src:
        src = html_lib.escape(logo_src, quote=True)
        logo = (
            f'<img class="hedron-browser-sim__logo" src="{src}" alt="" '
            'width="28" height="28" decoding="async" />'
        )
    url_text = html_lib.escape(url)
    cap = (
        f'<figcaption class="hedron-browser-sim__caption">{caption}</figcaption>' if caption else ""
    )
    return (
        '<figure class="hedron-browser-sim">'
        '<div class="hedron-browser-sim__chrome">'
        '<div class="hedron-browser-sim__titlebar">'
        '<div class="hedron-browser-sim__traffic" aria-hidden="true">'
        "<span></span><span></span><span></span></div>"
        '<div class="hedron-browser-sim__nav" aria-hidden="true">'
        '<span class="hedron-browser-sim__nav-btn">←</span>'
        '<span class="hedron-browser-sim__nav-btn">→</span>'
        '<span class="hedron-browser-sim__nav-btn hedron-browser-sim__nav-btn--keep">↻</span>'
        f'<div class="hedron-browser-sim__url"><span>ⓘ</span><code>{url_text}</code></div>'
        "</div></div>"
        '<div class="hedron-browser-sim__viewport">'
        f'<header class="hedron-browser-sim__brand">{logo}'
        '<span class="hedron-browser-sim__wordmark">Hedron</span></header>'
        f'<div class="hedron-browser-sim__page">{inner_html}</div>'
        "</div></div>"
        f"{cap}</figure>"
    )
