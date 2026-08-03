"""FastAPI-aware upload and download utility components."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from starlette.responses import FileResponse, Response

from hedron_core.component import Component
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.security import SafeUrl, UrlPurpose

__all__ = [
    "DownloadButton",
    "FileUpload",
    "safe_download_response",
    "validate_upload_filename",
]

_UNSAFE_FILENAME = re.compile(r"[^A-Za-z0-9._-]+")


def validate_upload_filename(name: str) -> str:
    base = Path(name).name
    if not base or base in {".", ".."} or "/" in name or "\\" in name:
        raise ValueError("Unsafe upload filename")
    cleaned = _UNSAFE_FILENAME.sub("_", base)
    if not cleaned or cleaned.startswith("."):
        raise ValueError("Unsafe upload filename")
    return cleaned


def safe_download_response(
    path: str | Path,
    *,
    filename: str,
    content_type: str = "application/octet-stream",
    authorized: bool = False,
) -> Response:
    if not authorized:
        raise PermissionError("Download requires authorization")
    safe_name = validate_upload_filename(filename)
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(str(file_path))
    # Prevent path disclosure in headers; only send basename.
    return FileResponse(
        path=file_path,
        media_type=content_type,
        filename=safe_name,
        headers={"Cache-Control": "private, no-store"},
    )


class FileUploadProps(Props):
    name: str = "file"
    accept: str | None = None
    maximum_size: int = 5_000_000
    multiple: bool = False
    label: str = "Upload file"


class FileUpload(Component[FileUploadProps]):
    props_type = FileUploadProps
    distribution = "hedron"
    logical_name = "FileUpload"

    def __init__(
        self,
        *,
        name: str = "file",
        accept: str | None = None,
        maximum_size: int = 5_000_000,
        multiple: bool = False,
        label: str = "Upload file",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            FileUploadProps(
                name=name,
                accept=accept,
                maximum_size=maximum_size,
                multiple=multiple,
                label=label,
                **kwargs,
            )
        )

    def render(self) -> Any:
        attrs: dict[str, Any] = {
            "type": "file",
            "name": self.props.name,
            "aria": {"label": self.props.label},
            "data": {"max-size": str(self.props.maximum_size)},
        }
        if self.props.accept:
            attrs["accept"] = self.props.accept
        if self.props.multiple:
            attrs["multiple"] = True
        return html.label(
            self.props.label,
            html.input(**attrs),
            class_="hedron-file-upload",
        )


class DownloadButtonProps(Props):
    href: SafeUrl
    filename: str
    label: str = "Download"


class DownloadButton(Component[DownloadButtonProps]):
    props_type = DownloadButtonProps
    distribution = "hedron"
    logical_name = "DownloadButton"

    def __init__(
        self,
        *,
        href: SafeUrl | str,
        filename: str,
        label: str = "Download",
        **kwargs: Any,
    ) -> None:
        validate_upload_filename(filename)
        url = (
            href
            if isinstance(href, SafeUrl)
            else SafeUrl.parse(href, purpose=UrlPurpose.NAVIGATION, allow_external=False)
        )
        super().__init__(DownloadButtonProps(href=url, filename=filename, label=label, **kwargs))

    def render(self) -> Any:
        return html.a(
            self.props.label,
            href=self.props.href,
            download=self.props.filename,
            class_="hedron-download-button",
            role="button",
        )
