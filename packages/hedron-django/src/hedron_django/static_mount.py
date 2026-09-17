"""Serve bundled Hedron static assets from ``hedron-core`` on Django."""

from __future__ import annotations

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBase
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
        if path.startswith("folio-accent/") and path.endswith(".css"):
            from hedron_core.diagnostics import HedronError
            from hedron_core.theme import emit_folio_accent_css

            try:
                css = emit_folio_accent_css(path.removeprefix("folio-accent/")[:-4])
            except HedronError as exc:
                raise Http404("Unknown Folio accent") from exc
            return HttpResponse(css, content_type="text/css")
        return serve(request, path, document_root=document_root)

    return [
        re_path(
            rf"^{clean}/(?P<path>.*)$",
            _serve,
            name="hedron_static",
        ),
    ]
