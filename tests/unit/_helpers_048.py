"""Helpers for phase 0.48 HTMX extension tests."""

from __future__ import annotations

from hedron_core.builtins import Page
from hedron_core.htmx_extensions import ExtensionPlan
from hedron_core.page_assets import inject_page_assets
from hedron_core.rendering import RenderMode, render


def render_page(node, *, mode: RenderMode = RenderMode.PAGE):
    return render(node, mode=mode)


def injected_page(*body, htmx_extensions=None, title: str = "Ext"):
    page = Page(*body, title=title, htmx_extensions=htmx_extensions)
    result = render_page(page)
    html = inject_page_assets(result.html, result.mode, plan=result.htmx_plan, assets=result.assets)
    plan = result.htmx_plan
    assert isinstance(plan, ExtensionPlan)
    return html, result
