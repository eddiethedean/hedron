"""Serve bundled Hedron static assets from ``hedron-core`` on Django."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponseBase
from django.urls import URLPattern, URLResolver, re_path
from django.views.static import serve

from hedron_core.page_assets import DEFAULT_STATIC_PREFIX, static_directory

__all__ = ["hedron_static_urlpatterns"]


def hedron_static_urlpatterns(
    *,
    prefix: str = DEFAULT_STATIC_PREFIX,
) -> list[URLPattern | URLResolver]:
    """URL patterns mounting bundled HTMX assets at ``/hedron-static/``."""
    clean = prefix.strip("/")
    document_root = str(static_directory())

    def _serve(request: HttpRequest, path: str) -> HttpResponseBase:
        return serve(request, path, document_root=document_root)

    return [
        re_path(
            rf"^{clean}/(?P<path>.*)$",
            _serve,
            name="hedron_static",
        ),
    ]
