"""Registered application stylesheet metadata."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from hedron_core.typing_aliases import JsonObject

_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]*$")
_SCOPE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
_LAYER = frozenset({"application", "overrides"})
_MEDIA = re.compile(r"^[A-Za-z0-9_() .:%-]+$")


def _digest_file(path: Path) -> str:
    return "sha256-" + hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class ApplicationStyleMeta:
    """One explicit, local application stylesheet."""

    logical_id: str
    name: str
    source: str
    owner: str = "application"
    scope: str | None = None
    layer: str = "application"
    global_: bool = False
    media: tuple[str, ...] = ()
    digest: str = ""
    provenance: str = ""

    def __post_init__(self) -> None:
        if not _NAME.fullmatch(self.name):
            raise ValueError("application style name must be a safe identifier")
        if self.scope is not None and not _SCOPE.fullmatch(self.scope):
            raise ValueError("application style scope must be a safe identifier")
        if self.scope is None and not self.global_:
            raise ValueError("application styles require scope or explicit global_=True")
        if self.layer not in _LAYER:
            raise ValueError(f"application style layer must be one of {sorted(_LAYER)}")
        if not self.source:
            raise ValueError("application style source is required")
        if any(
            not isinstance(item, str) or not item.strip() or _MEDIA.fullmatch(item.strip()) is None
            for item in self.media
        ):
            raise ValueError("application style media values must be safe media conditions")

    @property
    def path(self) -> Path:
        return Path(self.source)

    @property
    def source_digest(self) -> str:
        if self.digest:
            return self.digest
        return _digest_file(self.path) if self.path.is_file() else ""

    def to_dict(self) -> JsonObject:
        return {
            "logical_id": self.logical_id,
            "name": self.name,
            "source": self.source,
            "owner": self.owner,
            "scope": self.scope,
            "layer": self.layer,
            "global": self.global_,
            "media": list(self.media),
            "digest": self.source_digest,
            "provenance": self.provenance,
        }


def register_application_style(
    *,
    name: str,
    source: str | Path,
    scope: str | None = None,
    layer: str = "application",
    global_: bool = False,
    media: Sequence[str] = (),
    owner: str = "application",
    provenance: str = "",
) -> ApplicationStyleMeta:
    """Validate and register a local stylesheet in the existing registry."""
    path = Path(source).expanduser().resolve()
    if path.is_symlink():
        raise ValueError("application stylesheet symlinks are not allowed")
    if not path.is_file():
        raise FileNotFoundError(f"application stylesheet does not exist: {path}")
    meta = ApplicationStyleMeta(
        logical_id=f"{owner}:style:{name}",
        name=name,
        source=str(path),
        owner=owner,
        scope=scope,
        layer=layer,
        global_=global_,
        media=tuple(media),
        digest=_digest_file(path),
        provenance=provenance,
    )
    from hedron_core.registry.builder import active_builder

    active_builder().register_application_style(meta)
    return meta
