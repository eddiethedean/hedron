"""Directory upload validation (server-side)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import PurePosixPath
from urllib.parse import unquote

__all__ = ["DirectoryUploadFile", "validate_directory_upload"]


@dataclass(frozen=True, slots=True)
class DirectoryUploadFile:
    """Normalized directory-upload entry for server-side validation."""

    name: str
    size: int


def _as_upload_file(
    item: DirectoryUploadFile | tuple[str, int] | Mapping[str, object],
) -> DirectoryUploadFile:
    if isinstance(item, DirectoryUploadFile):
        return item
    if isinstance(item, tuple) and len(item) == 2:
        return DirectoryUploadFile(name=str(item[0]), size=int(item[1]))
    if isinstance(item, Mapping):
        return DirectoryUploadFile(name=str(item["name"]), size=int(item["size"]))  # type: ignore[index]
    raise TypeError(f"Unsupported directory upload entry: {type(item)!r}")


def _reject_traversal(path: str) -> None:
    if "\x00" in path:
        raise ValueError(f"Unsafe directory upload path: {path!r}")
    raw = path.replace("\\", "/")
    if "\x00" in raw:
        raise ValueError(f"Unsafe directory upload path: {path!r}")
    if not raw or raw.strip() != raw:
        raise ValueError(f"Unsafe directory upload path: {path!r}")
    if raw.startswith("/") or (len(raw) > 1 and raw[1] == ":"):
        raise ValueError(f"Absolute directory upload paths are not allowed: {path!r}")

    decoded = raw
    for _ in range(3):
        next_decoded = unquote(decoded)
        if next_decoded == decoded:
            break
        decoded = next_decoded
        if "\\" in decoded or any(ord(ch) < 32 for ch in decoded):
            raise ValueError(f"Unsafe directory upload path: {path!r}")
        if decoded.startswith("/") or (len(decoded) > 1 and decoded[1] == ":"):
            raise ValueError(f"Absolute directory upload paths are not allowed: {path!r}")

    for candidate in (raw, decoded):
        lowered = candidate.lower()
        if "%2e%2e" in lowered or "%2e." in lowered or ".%2e" in lowered:
            raise ValueError(f"Directory upload path traversal rejected: {path!r}")
        normalized = candidate.replace(";", "/")
        parts = [p for p in normalized.split("/") if p not in {"", "."}]
        if any(part == ".." or part.startswith("..") for part in parts):
            raise ValueError(f"Directory upload path traversal rejected: {path!r}")
        if any(part == "" for part in PurePosixPath(candidate.replace(";", "/")).parts):
            raise ValueError(f"Unsafe directory upload path: {path!r}")


def validate_directory_upload(
    files: Sequence[DirectoryUploadFile | tuple[str, int] | Mapping[str, object]],
    *,
    max_files: int,
    max_total_size: int,
) -> tuple[DirectoryUploadFile, ...]:
    """Validate directory upload names, counts, and total size (server-side)."""
    if max_files < 0:
        raise ValueError("max_files must be >= 0")
    if max_total_size < 0:
        raise ValueError("max_total_size must be >= 0")
    if len(files) > max_files:
        raise ValueError(f"Directory upload exceeds max_files={max_files}")
    validated: list[DirectoryUploadFile] = []
    total = 0
    for item in files:
        entry = _as_upload_file(item)
        _reject_traversal(entry.name)
        if entry.size < 0:
            raise ValueError(f"Negative file size for {entry.name!r}")
        total += entry.size
        if total > max_total_size:
            raise ValueError(f"Directory upload exceeds max_total_size={max_total_size}")
        validated.append(entry)
    return tuple(validated)
