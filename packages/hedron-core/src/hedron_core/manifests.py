"""Versioned build, asset, and CSS symbol manifests."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TypeVar

from typing_extensions import TypeIs

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


def _is_json_value(value: object) -> TypeIs[JsonValue]:
    if value is None or isinstance(value, (str, int, float, bool)):
        return True
    if isinstance(value, list):
        return all(_is_json_value(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(key, str) and _is_json_value(item) for key, item in value.items())
    return False


def _is_json_object(value: object) -> TypeIs[JsonObject]:
    return isinstance(value, dict) and all(
        isinstance(key, str) and _is_json_value(item) for key, item in value.items()
    )


def _as_json_object(value: object) -> JsonObject:
    """Narrow a decoded / dataclass mapping to ``JsonObject`` without cast."""
    if _is_json_object(value):
        return value
    if isinstance(value, Mapping):
        out: JsonObject = {}
        for key, item in value.items():
            if _is_json_value(item):
                out[str(key)] = item
            else:
                out[str(key)] = str(item)
        return out
    return {}


def _as_object_mapping(value: object) -> Mapping[str, JsonValue]:
    if _is_json_object(value):
        return value
    if isinstance(value, Mapping):
        return _as_json_object(value)
    return {}


def _as_object_sequence(value: object) -> Sequence[object]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return tuple(value)
    return ()


def _as_format_version(value: JsonValue) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value)
    if isinstance(value, float):
        return int(value)
    return int(str(value))


def _as_optional_str(value: JsonValue | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return str(value)


def canonical_json(value: JsonValue) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def load_json(path: Path) -> JsonValue:
    # json.loads is untyped; narrow at the JSON boundary.
    raw: object = json.loads(path.read_text(encoding="utf-8"))
    if _is_json_value(raw):
        return raw
    return str(raw)


def write_json_atomic(path: Path, value: JsonValue) -> str:
    """Write deterministic JSON via a unique same-dir temp file and atomic replace.

    Args:
        path: Destination path (parent directories are created as needed).
        value: JSON-compatible value serialized with sorted keys.

    Returns:
        Content digest of the written payload (including trailing newline).

    Raises:
        OSError: If the temp write or atomic replace fails after cleanup.
    """
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
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        tmp_path.replace(path)
    except Exception:
        with suppress(OSError):
            tmp_path.unlink(missing_ok=True)
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
        assets: list[JsonValue] = [
            _as_json_object(a.to_dict()) for a in sorted(self.assets, key=lambda x: x.logical_id)
        ]
        payload: JsonObject = {
            "format_version": self.format_version,
            "assets": assets,
        }
        digest = self.digest or content_digest(canonical_json(payload))
        return {**payload, "digest": digest}

    @classmethod
    def from_dict(cls, data: Mapping[str, JsonValue]) -> AssetManifest:
        assets = tuple(
            AssetEntry.from_dict(_as_object_mapping(item))
            for item in _as_object_sequence(data.get("assets", ()))
        )
        return cls(
            format_version=_as_format_version(data["format_version"]),
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
        payload: JsonObject = {
            "format_version": self.format_version,
            "component_id": self.component_id,
            "symbols": dict(sorted(self.symbols.items())),
            "keyframes": dict(sorted(self.keyframes.items())),
        }
        digest = self.digest or content_digest(canonical_json(payload))
        return {**payload, "digest": digest}

    @classmethod
    def from_dict(cls, data: Mapping[str, JsonValue]) -> CssSymbolManifest:
        return cls(
            format_version=_as_format_version(data["format_version"]),
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
        symbols: list[JsonValue] = [
            m.to_dict() for m in sorted(self.css_symbols, key=lambda m: m.component_id)
        ]
        payload: JsonObject = {
            "format_version": self.format_version,
            "theme": self.theme,
            "assets": self.assets.to_dict(),
            "css_symbols": symbols,
            "tool_versions": dict(sorted(self.tool_versions.items())),
            "config_digest": self.config_digest,
        }
        digest = self.digest or content_digest(canonical_json(payload))
        return {**payload, "digest": digest}

    @classmethod
    def from_dict(cls, data: Mapping[str, JsonValue]) -> BuildManifest:
        return cls(
            format_version=_as_format_version(data["format_version"]),
            theme=_as_optional_str(data.get("theme")),
            assets=AssetManifest.from_dict(_as_object_mapping(data["assets"])),
            css_symbols=tuple(
                CssSymbolManifest.from_dict(_as_object_mapping(item))
                for item in _as_object_sequence(data.get("css_symbols", ()))
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
        return _as_json_object(to_dict())
    # Fallback for plain dataclasses without to_dict.
    return _as_json_object(asdict(obj))  # type: ignore[arg-type]  # dataclass-only fallback


def ensure_sequence(items: Sequence[T]) -> tuple[T, ...]:
    return tuple(items)
