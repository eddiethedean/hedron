"""Component HTML response types."""

from __future__ import annotations

from collections.abc import Mapping

from fastapi.responses import HTMLResponse
from starlette.background import BackgroundTask

from hedron_core.component import NodeLike
from hedron_core.rendering import RenderMode

__all__ = [
    "ComponentResponse",
    "FileComponentResponse",
    "FragmentResponse",
    "HTML",
    "PageResponse",
    "_safe_content_disposition_filename",
]


class HTML:
    """Explicit HTML intent wrapper for plain FastAPI routes."""

    __slots__ = ("value", "mode")

    def __init__(self, value: NodeLike, *, mode: RenderMode | None = None) -> None:
        self.value = value
        self.mode = mode


class ComponentResponse(HTMLResponse):
    media_type = "text/html"


class PageResponse(ComponentResponse):
    pass


class FragmentResponse(ComponentResponse):
    pass


class FileComponentResponse(ComponentResponse):
    """File/download results produced through safe source contracts."""

    def __init__(
        self,
        content: str | bytes,
        *,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str = "application/octet-stream",
        filename: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        hdrs = dict(headers or {})
        if filename:
            safe_name = _safe_content_disposition_filename(filename)
            hdrs.setdefault("Content-Disposition", f'attachment; filename="{safe_name}"')
        super().__init__(
            content=content,
            status_code=status_code,
            headers=hdrs,
            media_type=media_type,
            background=background,
        )


def _safe_content_disposition_filename(filename: str) -> str:
    from hedron.builtins.files import validate_upload_filename

    try:
        return validate_upload_filename(filename)[:200]
    except ValueError:
        return "download"
