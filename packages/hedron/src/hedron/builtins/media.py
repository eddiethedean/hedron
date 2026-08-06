"""Authorized media delivery helpers (Range, disposition, download-all)."""

from __future__ import annotations

import zipfile
from collections.abc import Mapping, Sequence
from io import BytesIO
from pathlib import Path
from typing import Literal

from starlette.responses import FileResponse, Response

from hedron.builtins.files import validate_upload_filename

__all__ = [
    "ByteRangeNotSatisfiable",
    "download_all_zip",
    "media_file_response",
    "parse_byte_range",
]


class ByteRangeNotSatisfiable(ValueError):
    """Raised when a Range header is present but cannot be satisfied (HTTP 416)."""

    def __init__(self, size: int) -> None:
        self.size = size
        super().__init__(f"byte range not satisfiable for size={size}")


def parse_byte_range(header: str | None, *, size: int) -> tuple[int, int] | None:
    """Parse a single RFC 7233 ``bytes`` Range.

    Returns ``(start, end)`` inclusive, or ``None`` when the header is absent /
    ignored (non-bytes unit or multi-range → serve full entity). Raises
    :class:`ByteRangeNotSatisfiable` when the range cannot be satisfied.
    """
    if header is None:
        return None
    raw = header.strip()
    if not raw:
        return None
    if "=" not in raw:
        return None
    unit, _, spec = raw.partition("=")
    if unit.strip().lower() != "bytes":
        return None
    spec = spec.strip()
    if not spec or "," in spec:
        # Multi-range: Supported path serves the full entity (RFC allows this).
        return None
    if size <= 0:
        raise ByteRangeNotSatisfiable(size)

    if spec.startswith("-"):
        # suffix-length: last N bytes
        try:
            suffix = int(spec)
        except ValueError as exc:
            raise ByteRangeNotSatisfiable(size) from exc
        if suffix >= 0:
            raise ByteRangeNotSatisfiable(size)
        length = min(-suffix, size)
        start = size - length
        end = size - 1
        return start, end

    if "-" not in spec:
        raise ByteRangeNotSatisfiable(size)
    start_s, _, end_s = spec.partition("-")
    try:
        start = int(start_s) if start_s else 0
    except ValueError as exc:
        raise ByteRangeNotSatisfiable(size) from exc
    if start < 0 or start >= size:
        raise ByteRangeNotSatisfiable(size)
    if end_s == "":
        end = size - 1
    else:
        try:
            end = int(end_s)
        except ValueError as exc:
            raise ByteRangeNotSatisfiable(size) from exc
        if end < start:
            raise ByteRangeNotSatisfiable(size)
        end = min(end, size - 1)
    return start, end


def _resolve_jailed_file(path: str | Path, *, root: Path) -> Path:
    root_resolved = Path(root).resolve()
    file_path = Path(path).resolve()
    try:
        file_path.relative_to(root_resolved)
    except ValueError as exc:
        raise PermissionError("Download path escapes authorized root") from exc
    if not file_path.is_file():
        raise FileNotFoundError(str(file_path))
    return file_path


def _range_from_headers(
    request_headers: Mapping[str, str] | None,
    range_header: str | None,
) -> str | None:
    if range_header is not None:
        return range_header
    if request_headers is None:
        return None
    for key, value in request_headers.items():
        if key.lower() == "range":
            return value
    return None


def _content_disposition(disposition: Literal["inline", "attachment"], filename: str) -> str:
    safe = validate_upload_filename(filename)
    return f'{disposition}; filename="{safe}"'


def media_file_response(
    path: str | Path,
    *,
    root: Path,
    filename: str,
    content_type: str = "application/octet-stream",
    authorized: bool = False,
    request_headers: Mapping[str, str] | None = None,
    range_header: str | None = None,
    max_size: int | None = None,
    disposition: Literal["inline", "attachment"] = "inline",
) -> Response:
    """Serve a file with authz-before-bytes, path jail, and optional Range (206/416)."""
    if not authorized:
        raise PermissionError("Download requires authorization")
    file_path = _resolve_jailed_file(path, root=root)
    size = file_path.stat().st_size
    if max_size is not None and size > max_size:
        raise ValueError(f"Media file exceeds max_size of {max_size} bytes")

    safe_name = validate_upload_filename(filename)
    cache_headers = {
        "Cache-Control": "private, no-store",
        "Accept-Ranges": "bytes",
        "Content-Disposition": _content_disposition(disposition, safe_name),
    }

    header = _range_from_headers(request_headers, range_header)
    try:
        byte_range = parse_byte_range(header, size=size)
    except ByteRangeNotSatisfiable:
        return Response(
            status_code=416,
            headers={
                **cache_headers,
                "Content-Range": f"bytes */{size}",
            },
        )

    if byte_range is None:
        return FileResponse(
            path=file_path,
            media_type=content_type,
            headers=cache_headers,
        )

    start, end = byte_range
    length = end - start + 1
    with file_path.open("rb") as handle:
        handle.seek(start)
        payload = handle.read(length)
    return Response(
        content=payload,
        status_code=206,
        media_type=content_type,
        headers={
            **cache_headers,
            "Content-Range": f"bytes {start}-{end}/{size}",
            "Content-Length": str(length),
        },
    )


def download_all_zip(
    paths: Sequence[str | Path],
    *,
    root: Path,
    authorized: bool = False,
    max_total_bytes: int,
    filename: str = "download.zip",
) -> Response:
    """Budgeted zip of authorized paths under ``root``; reject when oversize."""
    if not authorized:
        raise PermissionError("Download requires authorization")
    if max_total_bytes < 0:
        raise ValueError("max_total_bytes cannot be negative")

    files: list[Path] = []
    total = 0
    for path in paths:
        file_path = _resolve_jailed_file(path, root=root)
        total += file_path.stat().st_size
        if total > max_total_bytes:
            raise ValueError(
                f"download-all archive exceeds max_total_bytes of {max_total_bytes} bytes"
            )
        files.append(file_path)

    buffer = BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in files:
            archive.write(file_path, arcname=file_path.name)
    payload = buffer.getvalue()

    safe_name = validate_upload_filename(filename)
    return Response(
        content=payload,
        media_type="application/zip",
        headers={
            "Cache-Control": "private, no-store",
            "Content-Disposition": _content_disposition("attachment", safe_name),
            "Content-Length": str(len(payload)),
        },
    )
