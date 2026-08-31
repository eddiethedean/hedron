"""Authorized media delivery helpers (Range, disposition, download-all)."""

from __future__ import annotations

import zipfile
from collections.abc import Iterator, Mapping, Sequence
from io import BytesIO
from pathlib import Path
from typing import Literal, cast

from starlette.responses import FileResponse, Response, StreamingResponse

from hedron.builtins.files import validate_upload_filename

__all__ = [
    "ByteRangeNotSatisfiable",
    "DEFAULT_MAX_RANGE_BYTES",
    "download_all_zip",
    "media_file_response",
    "parse_byte_range",
]

DEFAULT_MAX_RANGE_BYTES = 32 * 1024 * 1024
_RANGE_CHUNK_SIZE = 64 * 1024


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


def _iter_file_range(path: Path, start: int, length: int) -> Iterator[bytes]:
    remaining = length
    with path.open("rb") as handle:
        handle.seek(start)
        while remaining > 0:
            chunk = handle.read(min(_RANGE_CHUNK_SIZE, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk


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
    max_range_bytes: int | None = DEFAULT_MAX_RANGE_BYTES,
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
    range_budget = max_range_bytes
    if range_budget is not None and length > range_budget:
        raise ValueError(
            f"Requested Range length {length} exceeds max_range_bytes of {range_budget}"
        )
    return StreamingResponse(
        _iter_file_range(file_path, start, length),
        status_code=206,
        media_type=content_type,
        headers={
            **cache_headers,
            "Content-Range": f"bytes {start}-{end}/{size}",
            "Content-Length": str(length),
        },
    )


def _unique_arcnames(files: Sequence[Path], *, root: Path) -> list[tuple[Path, str]]:
    """Build deterministic unique ZIP member names relative to ``root`` (#104)."""
    root_resolved = root.resolve()
    used: set[str] = set()
    out: list[tuple[Path, str]] = []
    for file_path in files:
        rel = file_path.resolve().relative_to(root_resolved).as_posix()
        # Harden against absolute / traversal members.
        safe_parts = [p for p in rel.split("/") if p not in ("", ".", "..")]
        if not safe_parts:
            safe_parts = [file_path.name]
        arcname = "/".join(safe_parts)
        if arcname in used:
            raise ValueError(f"Duplicate archive member name {arcname!r}")
        used.add(arcname)
        out.append((file_path, arcname))
    return out


def download_all_zip(
    paths: Sequence[str | Path],
    *,
    root: Path,
    authorized: bool = False,
    max_total_bytes: int,
    max_members: int = 1_000,
    filename: str = "download.zip",
) -> Response:
    """Budgeted zip of authorized paths under ``root``; reject when oversize."""
    if not authorized:
        raise PermissionError("Download requires authorization")
    if max_total_bytes < 0:
        raise ValueError("max_total_bytes cannot be negative")
    member_limit = cast(object, max_members)
    if isinstance(member_limit, bool) or not isinstance(member_limit, int) or member_limit < 1:
        raise ValueError("max_members must be a positive integer")

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
        if len(files) > max_members:
            raise ValueError(f"download-all archive exceeds max_members of {max_members}")

    members = _unique_arcnames(files, root=Path(root))
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path, arcname in members:
            archive.write(file_path, arcname=arcname)
            if buffer.tell() > max_total_bytes:
                raise ValueError(
                    f"download-all archive exceeds max_total_bytes of {max_total_bytes} bytes"
                )
    payload = buffer.getvalue()
    if len(payload) > max_total_bytes:
        raise ValueError(f"download-all archive exceeds max_total_bytes of {max_total_bytes} bytes")

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
