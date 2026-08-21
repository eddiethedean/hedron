"""FastAPI-aware upload and download utility components."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from starlette.responses import FileResponse, Response

from hedron_core.builtins.appearance import Appearance, Density, Size, appearance_data
from hedron_core.component import Component
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.security import SafeUrl, UrlPurpose

__all__ = [
    "DownloadButton",
    "FileUpload",
    "safe_download_response",
    "validate_upload_filename",
    "validate_upload_size",
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


def validate_upload_size(size: int, *, maximum_size: int) -> int:
    """App-owned size gate for uploads (FileUpload.maximum_size is advisory markup)."""
    if size < 0:
        raise ValueError("Upload size cannot be negative")
    if size > maximum_size:
        raise ValueError(f"Upload exceeds maximum size of {maximum_size} bytes")
    return size


def safe_download_response(
    path: str | Path,
    *,
    root: Path,
    filename: str,
    content_type: str = "application/octet-stream",
    authorized: bool = False,
) -> Response:
    if not authorized:
        raise PermissionError("Download requires authorization")
    safe_name = validate_upload_filename(filename)
    root_resolved = Path(root).resolve()
    file_path = Path(path).resolve()
    try:
        file_path.relative_to(root_resolved)
    except ValueError as exc:
        raise PermissionError("Download path escapes authorized root") from exc
    if not file_path.is_file():
        raise FileNotFoundError(str(file_path))
    # Prevent path disclosure in headers; only send basename.
    return FileResponse(
        path=file_path,
        media_type=content_type,
        filename=safe_name,
        headers={"Cache-Control": "private, no-store"},
    )


def _format_size(maximum_size: int) -> str:
    if maximum_size >= 1_000_000:
        return f"{maximum_size / 1_000_000:.1f} MB"
    if maximum_size >= 1_000:
        return f"{maximum_size / 1_000:.0f} KB"
    return f"{maximum_size} B"


class FileUploadProps(Props):
    name: str = "file"
    accept: str | None = None
    maximum_size: int = 5_000_000
    multiple: bool = False
    label: str = "Upload file"
    hint: str | None = None
    status: str | None = None
    size: Size | None = None
    appearance: Appearance | None = None
    density: Density | None = None


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
        hint: str | None = None,
        status: str | None = None,
        size: Size | None = None,
        appearance: Appearance | None = None,
        density: Density | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            FileUploadProps(
                name=name,
                accept=accept,
                maximum_size=maximum_size,
                multiple=multiple,
                label=label,
                hint=hint,
                status=status,
                size=size,
                appearance=appearance,
                density=density,
                **kwargs,
            )
        )

    def render(self) -> Any:
        limit_text = f"Maximum size {_format_size(self.props.maximum_size)}"
        hint = self.props.hint or limit_text
        hint_id = f"hedron-file-upload-hint-{self.props.name}"
        status_id = f"hedron-file-upload-status-{self.props.name}"
        described_by = [hint_id]
        if self.props.status:
            described_by.append(status_id)
        input_attrs: dict[str, Any] = {
            "type": "file",
            "name": self.props.name,
            "aria": {"label": self.props.label, "describedby": " ".join(described_by)},
            "data": {"max-size": str(self.props.maximum_size)},
            "class_": "hedron-file-upload-input",
        }
        if self.props.accept:
            input_attrs["accept"] = self.props.accept
        if self.props.multiple:
            input_attrs["multiple"] = True
        parts: list[Any] = [
            html.span(self.props.label, class_="hedron-file-upload-label"),
            html.input(**input_attrs),
            html.span(hint, id=hint_id, class_="hedron-file-upload-hint"),
        ]
        if self.props.status:
            parts.append(
                html.span(
                    self.props.status,
                    id=status_id,
                    class_="hedron-file-upload-status",
                    role="status",
                )
            )
        data = {
            "hedron-file-upload": "true",
            "max-size": str(self.props.maximum_size),
            **appearance_data(
                size=self.props.size,
                appearance=self.props.appearance,
                density=self.props.density,
            ),
        }
        return html.label(
            *parts,
            class_="hedron-file-upload",
            data=data,
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
        href: SafeUrl | str | None = None,
        filename: str,
        label: str = "Download",
        source: SafeUrl | str | None = None,
        **kwargs: Any,
    ) -> None:
        validate_upload_filename(filename)
        target = href if href is not None else source
        if target is None:
            raise ValueError("DownloadButton requires href= or source=")
        url = (
            target
            if isinstance(target, SafeUrl)
            else SafeUrl.parse(target, purpose=UrlPurpose.NAVIGATION, allow_external=False)
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
