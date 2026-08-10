"""Versioned build, asset, and CSS symbol manifests."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TypeVar, cast

from hedron_core.identifiers import content_digest
from hedron_core.typing_aliases import AssetEntryDict, JsonObject, JsonValue

T = TypeVar("T")

__all__ = [
    "ASSET_MANIFEST_FORMAT",
    "BUILD_MANIFEST_FORMAT",
    "CSS_SYMBOL_MANIFEST_FORMAT",
    "AssetEntry",
    "AssetManifest",
    "BuildManifest",
    "CssSymbolManifest",
    "canonical_json",
    "load_json",
    "write_json_atomic",
]

BUILD_MANIFEST_FORMAT = 2
ASSET_MANIFEST_FORMAT = 1
CSS_SYMBOL_MANIFEST_FORMAT = 1


def _as_str_map(value: JsonValue | None) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {str(k): str(v) for k, v in value.items()}


def canonical_json(value: JsonValue) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def load_json(path: Path) -> JsonValue:
    return cast(JsonValue, json.loads(path.read_text(encoding="utf-8")))


def write_json_atomic(path: Path, value: JsonValue) -> str:
    """Write deterministic JSON via a unique same-dir temp file and os.replace."""
    import os
    import tempfile
    from contextlib import suppress

    path.parent.mkdir(parents=True, exist_ok=True)
    text = canonical_json(value) + "\n"
    digest = content_digest(text)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except Exception:
        with suppress(OSError):
            os.unlink(tmp_name)
        raise
    return digest


@dataclass(frozen=True, slots=True)
class AssetEntry:
    logical_id: str
    kind: str  # css | js | module | media | font | other — open host vocabulary
    path: str
    digest: str
    content_type: str
    attributes: Mapping[str, str] = field(default_factory=dict)

    def to_dict(self) -> AssetEntryDict:
        return {
            "logical_id": self.logical_id,
            "kind": self.kind,
            "path": self.path,
            "digest": self.digest,
            "content_type": self.content_type,
            "attributes": dict(self.attributes),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, JsonValue]) -> AssetEntry:
        return cls(
            logical_id=str(data["logical_id"]),
            kind=str(data["kind"]),
            path=str(data["path"]),
            digest=str(data["digest"]),
            content_type=str(data["content_type"]),
            attributes=_as_str_map(data.get("attributes")),
        )


@dataclass(frozen=True, slots=True)
class AssetManifest:
    format_version: int
    assets: tuple[AssetEntry, ...]
    digest: str = ""

    def to_dict(self) -> JsonObject:
        payload = cast(
            JsonObject,
            {
                "format_version": self.format_version,
                "assets": [a.to_dict() for a in sorted(self.assets, key=lambda x: x.logical_id)],
            },
        )
        digest = self.digest or content_digest(canonical_json(payload))
        return {**payload, "digest": digest}

    @classmethod
    def from_dict(cls, data: Mapping[str, JsonValue]) -> AssetManifest:
        assets = tuple(
            AssetEntry.from_dict(cast(Mapping[str, JsonValue], item))
            for item in cast(Sequence[object], data.get("assets", ()))
        )
        return cls(
            format_version=int(cast(int | str, data["format_version"])),
            assets=assets,
            digest=str(data.get("digest") or ""),
        )

    def validate_format(self) -> None:
        if self.format_version != ASSET_MANIFEST_FORMAT:
            from hedron_core.diagnostics import error

            raise error(
                "HED-ASSET-0001",
                title="Unsupported asset manifest version",
                explanation=(
                    f"Asset manifest format {self.format_version} is not supported "
                    f"(expected {ASSET_MANIFEST_FORMAT})."
                ),
                remediation="Rebuild with a compatible Hedron release.",
            )


@dataclass(frozen=True, slots=True)
class CssSymbolManifest:
    format_version: int
    component_id: str
    symbols: Mapping[str, str]  # authored name -> scoped identifier
    keyframes: Mapping[str, str]
    digest: str = ""

    def to_dict(self) -> JsonObject:
        payload = cast(
            JsonObject,
            {
                "format_version": self.format_version,
                "component_id": self.component_id,
                "symbols": dict(sorted(self.symbols.items())),
                "keyframes": dict(sorted(self.keyframes.items())),
            },
        )
        digest = self.digest or content_digest(canonical_json(payload))
        return {**payload, "digest": digest}

    @classmethod
    def from_dict(cls, data: Mapping[str, JsonValue]) -> CssSymbolManifest:
        return cls(
            format_version=int(cast(int | str, data["format_version"])),
            component_id=str(data["component_id"]),
            symbols=_as_str_map(data.get("symbols")),
            keyframes=_as_str_map(data.get("keyframes")),
            digest=str(data.get("digest") or ""),
        )

    def validate_format(self) -> None:
        if self.format_version != CSS_SYMBOL_MANIFEST_FORMAT:
            from hedron_core.diagnostics import error

            raise error(
                "HED-CSS-0001",
                title="Unsupported CSS symbol manifest version",
                explanation=(
                    f"CSS symbol manifest format {self.format_version} is not supported "
                    f"(expected {CSS_SYMBOL_MANIFEST_FORMAT})."
                ),
                remediation="Rebuild with a compatible Hedron release.",
            )


@dataclass(frozen=True, slots=True)
class BuildManifest:
    format_version: int
    theme: str | None
    assets: AssetManifest
    css_symbols: tuple[CssSymbolManifest, ...]
    tool_versions: Mapping[str, str]
    config_digest: str
    digest: str = ""

    def to_dict(self) -> JsonObject:
        payload = cast(
            JsonObject,
            {
                "format_version": self.format_version,
                "theme": self.theme,
                "assets": self.assets.to_dict(),
                "css_symbols": [
                    m.to_dict() for m in sorted(self.css_symbols, key=lambda m: m.component_id)
                ],
                "tool_versions": dict(sorted(self.tool_versions.items())),
                "config_digest": self.config_digest,
            },
        )
        digest = self.digest or content_digest(canonical_json(payload))
        return {**payload, "digest": digest}

    @classmethod
    def from_dict(cls, data: Mapping[str, JsonValue]) -> BuildManifest:
        return cls(
            format_version=int(cast(int | str, data["format_version"])),
            theme=cast(str | None, data.get("theme")),
            assets=AssetManifest.from_dict(cast(Mapping[str, JsonValue], data["assets"])),
            css_symbols=tuple(
                CssSymbolManifest.from_dict(cast(Mapping[str, JsonValue], item))
                for item in cast(Sequence[object], data.get("css_symbols", ()))
            ),
            tool_versions=_as_str_map(data.get("tool_versions")),
            config_digest=str(data.get("config_digest") or ""),
            digest=str(data.get("digest") or ""),
        )

    def validate_format(self) -> None:
        if self.format_version != BUILD_MANIFEST_FORMAT:
            from hedron_core.diagnostics import error

            raise error(
                "HED-BUILD-0001",
                title="Unsupported build manifest version",
                explanation=(
                    f"Build manifest format {self.format_version} is not supported "
                    f"(expected {BUILD_MANIFEST_FORMAT})."
                ),
                remediation="Rebuild with a compatible Hedron release.",
            )
        self.assets.validate_format()
        for sym in self.css_symbols:
            sym.validate_format()


def manifest_as_dict(obj: object) -> JsonObject:
    to_dict = getattr(obj, "to_dict", None)
    if callable(to_dict):
        # Host/dataclass to_dict may be untyped; JsonObject is the wire contract.
        return cast(JsonObject, to_dict())
    # Fallback for plain dataclasses without to_dict.
    return cast(JsonObject, asdict(obj))  # type: ignore[arg-type]  # dataclass-only fallback


def ensure_sequence(items: Sequence[T]) -> tuple[T, ...]:
    return tuple(items)
