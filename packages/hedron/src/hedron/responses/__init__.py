"""Component HTML response helpers."""

from __future__ import annotations

from hedron.responses.assets import (
    _inject_htmx_extension_assets as _inject_htmx_extension_assets,
)
from hedron.responses.html import HTML as HTML
from hedron.responses.html import ComponentResponse as ComponentResponse
from hedron.responses.html import FileComponentResponse as FileComponentResponse
from hedron.responses.html import FragmentResponse as FragmentResponse
from hedron.responses.html import PageResponse as PageResponse
from hedron.responses.html import (
    _safe_content_disposition_filename as _safe_content_disposition_filename,
)
from hedron.responses.render import (
    _apply_auth_cache_headers as _apply_auth_cache_headers,
)
from hedron.responses.render import fragment_region_http_detail as fragment_region_http_detail
from hedron.responses.render import hedron_response as hedron_response
from hedron.responses.render import merge_htmx_headers as merge_htmx_headers
from hedron.responses.render import (
    render_component_response as render_component_response,
)
from hedron.responses.render import render_interaction as render_interaction

_fragment_region_http_detail = fragment_region_http_detail

__all__ = [
    "ComponentResponse",
    "FileComponentResponse",
    "FragmentResponse",
    "HTML",
    "PageResponse",
    "hedron_response",
    "fragment_region_http_detail",
    "merge_htmx_headers",
    "render_component_response",
    "render_interaction",
]
