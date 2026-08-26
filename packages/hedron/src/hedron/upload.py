"""Typed multipart / file-upload lifecycle (UPLOAD-055)."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from hedron.builtins.files import validate_upload_filename, validate_upload_size

__all__ = [
    "UploadBudget",
    "UploadField",
    "UploadHandle",
    "cleanup_upload",
    "materialize_upload",
    "read_upload_capped",
    "validate_upload_batch",
]


@dataclass(frozen=True, slots=True)
class UploadBudget:
    maximum_size: int = 5_000_000
    maximum_count: int = 1
    maximum_filename_bytes: int = 255
    allowed_extensions: tuple[str, ...] = ()
    allowed_content_types: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class UploadField:
    """Declarative upload constraints (beta). Markup still uses FileUpload."""

    name: str = "file"
    budget: UploadBudget = field(default_factory=UploadBudget)
    required: bool = True


@dataclass(slots=True)
class UploadHandle:
    """Framework-owned temporary upload until the handler accepts transfer."""

    filename: str
    content_type: str | None
    size: int
    path: Path
    owned: bool = True

    def accept(self) -> Path:
        """Transfer ownership to the application; framework will not delete."""
        self.owned = False
        return self.path

    def cleanup(self) -> None:
        if not self.owned:
            return
        try:
            self.path.unlink()
        except FileNotFoundError:
            self.owned = False
        except OSError:
            # Preserve ownership so a transient filesystem failure can be retried.
            return
        else:
            self.owned = False


def cleanup_upload(handle: UploadHandle | None) -> None:
    if handle is not None:
        handle.cleanup()


async def read_upload_capped(
    file: object,
    *,
    maximum_size: int,
    chunk_size: int = 64 * 1024,
) -> bytes:
    """Read an UploadFile-like object up to ``maximum_size`` bytes (fail closed).

    Rejects before allocating the full body when the stream exceeds the budget.
    """
    import inspect

    if maximum_size < 0:
        raise ValueError("Upload size budget must be non-negative")
    read = getattr(file, "read", None)
    if not callable(read):
        raise ValueError("Upload stream does not support read()")
    chunks: list[bytes] = []
    total = 0
    while True:
        raw = read(chunk_size)
        piece = await raw if inspect.isawaitable(raw) else raw
        if not piece:
            break
        if not isinstance(piece, (bytes, bytearray)):
            raise ValueError("Upload stream returned non-bytes")
        total += len(piece)
        if total > maximum_size:
            raise ValueError(f"Upload exceeds maximum size of {maximum_size} bytes")
        chunks.append(bytes(piece))
    return b"".join(chunks)


def materialize_upload(
    *,
    filename: str,
    content: bytes,
    content_type: str | None = None,
    budget: UploadBudget | None = None,
) -> UploadHandle:
    limits = budget or UploadBudget()
    safe = validate_upload_filename(filename)
    if len(safe.encode("utf-8")) > limits.maximum_filename_bytes:
        raise ValueError("Upload filename exceeds budget")
    validate_upload_size(len(content), maximum_size=limits.maximum_size)
    if limits.allowed_extensions:
        allowed = {
            e.lower() if e.startswith(".") else f".{e.lower()}" for e in limits.allowed_extensions
        }
        ext = Path(safe).suffix.lower()
        if ext not in allowed:
            raise ValueError("Upload extension is not allowed")
    if limits.allowed_content_types:
        if not content_type:
            raise ValueError("Upload content type is required")
        normalized = content_type.split(";", 1)[0].strip().lower()
        if normalized not in {c.lower() for c in limits.allowed_content_types}:
            raise ValueError("Upload content type is not allowed")
    fd, name = tempfile.mkstemp(prefix="hedron-upload-", suffix=Path(safe).suffix)
    path = Path(name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return UploadHandle(
        filename=safe,
        content_type=content_type,
        size=len(content),
        path=path,
        owned=True,
    )


def validate_upload_batch(handles: Sequence[UploadHandle], budget: UploadBudget) -> None:
    if len(handles) > budget.maximum_count:
        raise ValueError(f"Upload count exceeds maximum of {budget.maximum_count}")
