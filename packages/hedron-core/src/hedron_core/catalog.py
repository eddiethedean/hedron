"""Portable interaction catalog, manifest, and package projections (phase 0.45).

Values are framework-neutral. The catalog indexes 0.43 descriptors and optional
0.44 TypeSchema extensions. It never routes, validates, authorizes, executes, or
exposes anything.

The compatibility helpers retain a process-level fallback, while application
runtimes bind projection providers and sealed catalogs through context-local
state.
"""

from __future__ import annotations

import hashlib
import json
import re
import threading
from collections.abc import Generator, Mapping, Sequence
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Literal, Protocol, cast, runtime_checkable

from hedron_core.codes import (
    HED_CATALOG_0001,
    HED_CATALOG_0002,
    HED_CATALOG_0003,
    HED_CATALOG_0004,
    HED_CATALOG_0005,
    HED_CATALOG_0006,
    HED_CATALOG_0007,
    HED_CATALOG_0008,
    HED_PROJECTION_0001,
    HED_PROJECTION_0002,
    HED_PROJECTION_0004,
    HED_PROJECTION_0006,
)
from hedron_core.diagnostics import (
    DiagnosticSeverity,
    HedronError,
    make_diagnostic,
)
from hedron_core.manifests import canonical_json, write_json_atomic
from hedron_core.type_schema import (
    TYPE_SCHEMA_NAMESPACE,
    payload_fingerprint,
    redact_type_payload,
    type_schema_from_descriptor,
)
from hedron_core.typing_aliases import JsonObject, JsonValue, is_object_list, is_string_mapping
from hedron_core.updates import (
    BaseHandleDescriptor,
    descriptor_fingerprint,
    list_handle_descriptors,
)

CATALOG_SCHEMA_VERSION = 1
MANIFEST_FORMAT_VERSION = 1
PROJECTION_SCHEMA_VERSION = 1

MAX_CATALOG_ENTRIES = 4096
MAX_PROJECTIONS = 256
MAX_PROJECTION_BYTES = 65_536
MAX_MANIFEST_BYTES = 2_000_000
MAX_DIAGNOSTICS = 256
MAX_STRING_LENGTH = 4096
MAX_NESTING = 16
MAX_LIMITATIONS = 64

HandleKind = Literal["view", "command"]
EffectState = Literal["dynamic", "observed", "declared"]
RedactionProfile = Literal["production", "development", "conformance"]
ProjectionDisposition = Literal[
    "native_consumer",
    "projection_adapter",
    "compatibility_only",
    "not_applicable",
]
ProjectionSupport = Literal["supported", "experimental", "unavailable", "unknown"]

FORBIDDEN_KEYS = frozenset(
    {
        "values",
        "defaults",
        "examples",
        "callbacks",
        "request",
        "model",
        "credentials",
        "session",
        "handler",
        "code",
        "executable",
        "secret",
        "password",
        "token",
        "cookie",
    }
)
PRODUCTION_FORBIDDEN_KEYS = FORBIDDEN_KEYS | {"source_path", "source", "file_path", "filename"}
RESERVED_PROJECTION_NAMESPACES = frozenset(
    {
        TYPE_SCHEMA_NAMESPACE,
        "path",
        "method",
        "app_id",
        "logical_id",
        "host",
        "target",
        "fallback",
        "limits",
        "swap",
        "region",
    }
)
_NAMESPACE_RE = re.compile(r"^[a-z][a-z0-9_-]*(\.[a-z0-9_-]+)+$")
_FINGERPRINT_RE = re.compile(r"^[0-9a-f]{32}$")

__all__ = [
    "CATALOG_SCHEMA_VERSION",
    "CatalogEntry",
    "CatalogVersionError",
    "InteractionCatalog",
    "InteractionManifest",
    "MANIFEST_FORMAT_VERSION",
    "MAX_CATALOG_ENTRIES",
    "MAX_MANIFEST_BYTES",
    "MAX_PROJECTIONS",
    "PackageProjection",
    "ProjectionCapability",
    "ProjectionDisposition",
    "ProjectionProvider",
    "SurfaceProjectionProvider",
    "catalog_fingerprint",
    "compile_interaction_catalog",
    "entry_from_descriptor",
    "get_sealed_catalog",
    "new_projection_registry",
    "use_catalog_context",
    "use_projection_registry",
    "list_projection_providers",
    "register_projection_provider",
    "reset_catalog_for_tests",
    "seal_interaction_catalog",
    "unregister_projection_provider",
]


class CatalogVersionError(HedronError):
    """Manifest, catalog, or projection version / fingerprint mismatch."""


def _catalog_error(
    code: str,
    *,
    title: str,
    explanation: str,
    remediation: str,
) -> CatalogVersionError:
    return CatalogVersionError(
        make_diagnostic(
            code,
            severity=DiagnosticSeverity.ERROR,
            title=title,
            explanation=explanation,
            remediation=remediation,
        )
    )


catalog_error = _catalog_error


def catalog_fingerprint(payload: object) -> str:
    encoded = canonical_json(cast(JsonValue, payload))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:32]


def _empty_json_object() -> JsonObject:
    return {}


def _empty_string_mapping() -> dict[str, str]:
    return {}


def _empty_projection_mapping() -> dict[str, PackageProjection]:
    return {}


def _empty_entry_mapping() -> dict[str, CatalogEntry]:
    return {}


def _assert_bounds(value: object, *, depth: int = 0) -> None:
    if depth > MAX_NESTING:
        raise _catalog_error(
            HED_CATALOG_0005,
            title="Catalog nesting limit exceeded",
            explanation=f"JSON nesting exceeded {MAX_NESTING}.",
            remediation="Reduce projection/manifest nesting.",
        )
    if isinstance(value, str) and len(value) > MAX_STRING_LENGTH:
        raise _catalog_error(
            HED_CATALOG_0005,
            title="Catalog string limit exceeded",
            explanation=f"String length {len(value)} exceeds {MAX_STRING_LENGTH}.",
            remediation="Bound diagnostic and projection strings.",
        )
    if isinstance(value, Mapping):
        mapping = cast(Mapping[object, object], value)
        if len(mapping) > MAX_CATALOG_ENTRIES:
            raise _catalog_error(
                HED_CATALOG_0005,
                title="Catalog mapping limit exceeded",
                explanation=f"Mapping has {len(mapping)} keys.",
                remediation="Split the catalog payload.",
            )
        for key, item in mapping.items():
            _assert_bounds(str(key), depth=depth + 1)
            _assert_bounds(item, depth=depth + 1)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        sequence = cast(Sequence[object], value)
        if len(sequence) > MAX_CATALOG_ENTRIES:
            raise _catalog_error(
                HED_CATALOG_0005,
                title="Catalog sequence limit exceeded",
                explanation=f"Sequence has {len(sequence)} items.",
                remediation="Reduce entry or projection volume.",
            )
        for item in sequence:
            _assert_bounds(item, depth=depth + 1)


def _walk_forbidden(payload: object, *, production: bool) -> None:
    forbidden = PRODUCTION_FORBIDDEN_KEYS if production else FORBIDDEN_KEYS
    if isinstance(payload, Mapping):
        mapping = cast(Mapping[object, object], payload)
        overlap = forbidden.intersection(str(key) for key in mapping)
        if overlap:
            raise _catalog_error(
                HED_CATALOG_0008,
                title="Forbidden catalog keys",
                explanation=f"Payload contains forbidden keys {sorted(overlap)}.",
                remediation="Redact values/defaults/examples/callbacks before serialization.",
            )
        for item in mapping.values():
            _walk_forbidden(item, production=production)
    elif isinstance(payload, Sequence) and not isinstance(payload, (str, bytes)):
        sequence = cast(Sequence[object], payload)
        for item in sequence:
            _walk_forbidden(item, production=production)


@dataclass(frozen=True, slots=True)
class ProjectionCapability:
    name: str
    support: ProjectionSupport = "supported"
    limitation: str = ""

    def as_mapping(self) -> JsonObject:
        payload: JsonObject = {"name": self.name, "support": self.support}
        if self.limitation:
            payload["limitation"] = self.limitation
        return payload


@dataclass(frozen=True, slots=True)
class PackageProjection:
    namespace: str
    schema_version: int = PROJECTION_SCHEMA_VERSION
    provider: str = ""
    provider_version: str = ""
    catalog_fingerprint: str = ""
    entry_fingerprint: str | None = None
    capabilities: tuple[ProjectionCapability, ...] = ()
    data: Mapping[str, JsonValue] = field(default_factory=_empty_json_object)
    limitations: tuple[str, ...] = ()
    disposition: ProjectionDisposition = "native_consumer"

    def __post_init__(self) -> None:
        object.__setattr__(self, "data", dict(self.data))
        if self.namespace in RESERVED_PROJECTION_NAMESPACES or not _NAMESPACE_RE.fullmatch(
            self.namespace
        ):
            raise _catalog_error(
                HED_PROJECTION_0001,
                title="Invalid projection namespace",
                explanation=f"Namespace {self.namespace!r} is reserved or malformed.",
                remediation="Use reverse-DNS or a Hedron-reserved dotted namespace.",
            )
        encoded = canonical_json(cast(JsonValue, dict(self.data)))
        if len(encoded.encode("utf-8")) > MAX_PROJECTION_BYTES:
            raise _catalog_error(
                HED_PROJECTION_0002,
                title="Projection data exceeds byte bound",
                explanation=f"Projection {self.namespace!r} exceeds {MAX_PROJECTION_BYTES} bytes.",
                remediation="Reduce projection data; keep current-surface facts only.",
            )
        _assert_bounds(self.data)
        _walk_forbidden(self.data, production=True)

    def as_mapping(self) -> JsonObject:
        payload: JsonObject = {
            "namespace": self.namespace,
            "schema_version": self.schema_version,
            "provider": self.provider,
            "provider_version": self.provider_version,
            "catalog_fingerprint": self.catalog_fingerprint,
            "capabilities": [item.as_mapping() for item in self.capabilities],
            "data": dict(self.data),
            "limitations": list(self.limitations),
            "disposition": self.disposition,
        }
        if self.entry_fingerprint is not None:
            payload["entry_fingerprint"] = self.entry_fingerprint
        payload["fingerprint"] = catalog_fingerprint(payload)
        return payload


@runtime_checkable
class ProjectionProvider(Protocol):
    namespace: str

    def project(
        self,
        entries: Sequence[CatalogEntry],
        *,
        catalog_fingerprint: str,
        trusted: bool = True,
    ) -> tuple[PackageProjection, ...]: ...


@dataclass(frozen=True, slots=True)
class SurfaceProjectionProvider:
    """Current-surface projection describing an optional package API."""

    namespace: str
    provider: str
    provider_version: str
    surface: str
    schema_version: int = PROJECTION_SCHEMA_VERSION
    limitations: tuple[str, ...] = ()
    disposition: ProjectionDisposition = "native_consumer"

    def project(
        self,
        entries: Sequence[CatalogEntry],
        *,
        catalog_fingerprint: str,
        trusted: bool = True,
    ) -> tuple[PackageProjection, ...]:
        if not trusted:
            raise _catalog_error(
                HED_PROJECTION_0004,
                title="Untrusted projection provider",
                explanation=f"Provider {self.provider!r} was invoked outside trusted registration.",
                remediation="Run providers only during plugin registration or `hedron build`.",
            )
        del entries
        return (
            PackageProjection(
                namespace=self.namespace,
                schema_version=self.schema_version,
                provider=self.provider,
                provider_version=self.provider_version,
                catalog_fingerprint=catalog_fingerprint,
                capabilities=(ProjectionCapability(name=self.surface, support="supported"),),
                data={
                    "surface": self.surface,
                    "direct_apis": True,
                    "catalog_required": False,
                    "exposure": False,
                },
                limitations=self.limitations,
                disposition=self.disposition,
            ),
        )


@dataclass(frozen=True, slots=True)
class CatalogEntry:
    logical_id: str
    kind: HandleKind
    descriptor_version: int
    descriptor_fingerprint: str
    effect_state: EffectState = "dynamic"
    type_schema_version: int | None = None
    type_schema_fingerprint: str | None = None
    handler_fingerprint: str | None = None
    model_fingerprint: str | None = None
    boundary_sources: tuple[str, ...] = ()
    field_paths: tuple[Mapping[str, JsonValue], ...] = ()
    control_dispositions: Mapping[str, str] = field(default_factory=_empty_string_mapping)
    sensitivity_flags: tuple[str, ...] = ()
    identity_flags: tuple[str, ...] = ()
    declared_target_ids: tuple[str, ...] = ()
    outcome_variant_ids: tuple[str, ...] = ()
    projections: Mapping[str, PackageProjection] = field(default_factory=_empty_projection_mapping)
    limitations: tuple[str, ...] = ()
    provenance: Mapping[str, JsonValue] = field(default_factory=_empty_json_object)

    def __post_init__(self) -> None:
        object.__setattr__(self, "control_dispositions", dict(self.control_dispositions))
        object.__setattr__(self, "projections", dict(self.projections))
        object.__setattr__(self, "provenance", dict(self.provenance))
        object.__setattr__(self, "field_paths", tuple(dict(item) for item in self.field_paths))
        if self.kind not in {"view", "command"}:
            raise _catalog_error(
                HED_CATALOG_0001,
                title="Invalid catalog kind",
                explanation=f"kind {self.kind!r} is not a 0.43 handle kind.",
                remediation="Index BaseHandleDescriptor.kind only (view or command).",
            )
        if not _FINGERPRINT_RE.fullmatch(self.descriptor_fingerprint):
            raise _catalog_error(
                HED_CATALOG_0001,
                title="Invalid descriptor fingerprint",
                explanation="Descriptor fingerprints are SHA-256 first 32 hex chars.",
                remediation="Use descriptor_fingerprint() from the 0.43 descriptor.",
            )

    def as_mapping(self, *, profile: RedactionProfile = "production") -> JsonObject:
        payload: JsonObject = {
            "logical_id": self.logical_id,
            "kind": self.kind,
            "descriptor_version": self.descriptor_version,
            "descriptor_fingerprint": self.descriptor_fingerprint,
            "effect_state": self.effect_state,
        }
        if self.type_schema_version is not None:
            payload["type_schema_version"] = self.type_schema_version
        if self.type_schema_fingerprint is not None:
            payload["type_schema_fingerprint"] = self.type_schema_fingerprint
        if self.handler_fingerprint:
            payload["handler_fingerprint"] = self.handler_fingerprint
        if self.model_fingerprint:
            payload["model_fingerprint"] = self.model_fingerprint
        if self.boundary_sources:
            payload["boundary_sources"] = list(self.boundary_sources)
        if self.field_paths:
            payload["field_paths"] = [dict(item) for item in self.field_paths]
        if self.control_dispositions:
            payload["control_dispositions"] = dict(self.control_dispositions)
        if self.sensitivity_flags:
            payload["sensitivity_flags"] = list(self.sensitivity_flags)
        if self.identity_flags:
            payload["identity_flags"] = list(self.identity_flags)
        if self.declared_target_ids:
            payload["declared_target_ids"] = list(self.declared_target_ids)
        if self.outcome_variant_ids:
            payload["outcome_variant_ids"] = list(self.outcome_variant_ids)
        if self.projections:
            payload["projections"] = {
                name: projection.as_mapping()
                for name, projection in sorted(self.projections.items())
            }
        if self.limitations:
            payload["limitations"] = list(self.limitations)
        provenance = dict(self.provenance)
        if profile == "production":
            for key in ("source_path", "source", "file_path", "filename"):
                provenance.pop(key, None)
        if profile == "conformance":
            provenance = {k: v for k, v in provenance.items() if k in {"app_id", "unknown"}}
        if provenance:
            payload["provenance"] = provenance
        payload["fingerprint"] = catalog_fingerprint(
            {key: value for key, value in payload.items() if key != "fingerprint"}
        )
        _walk_forbidden(payload, production=profile == "production")
        return payload


def entry_from_descriptor(descriptor: BaseHandleDescriptor) -> CatalogEntry:
    """Compile one redacted catalog entry from a live 0.43 descriptor."""
    schema = type_schema_from_descriptor(descriptor)
    raw_type = descriptor.extensions.get(TYPE_SCHEMA_NAMESPACE)
    type_version: int | None = None
    type_fp: str | None = None
    handler_fp: str | None = None
    model_fp: str | None = None
    boundary: tuple[str, ...] = ()
    field_paths: tuple[Mapping[str, JsonValue], ...] = ()
    dispositions: Mapping[str, str] = {}
    sensitivity: tuple[str, ...] = ()
    identity: tuple[str, ...] = ()
    declared: tuple[str, ...] = ()
    outcomes: tuple[str, ...] = ()
    if schema is not None:
        type_version = schema.schema_version
        if isinstance(raw_type, Mapping):
            type_fp = payload_fingerprint(
                redact_type_payload({str(key): value for key, value in raw_type.items()})
            )
        else:
            type_fp = schema.stable_fingerprint()
        handler_fp = schema.handler_fingerprint or None
        model_fp = schema.model_fingerprint or None
        boundary = tuple(schema.boundary_sources)
        field_paths = tuple(schema.field_paths)
        dispositions = dict(schema.control_dispositions)
        sensitivity = tuple(schema.sensitivity_flags)
        identity = tuple(schema.identity_flags)
        declared = tuple(schema.declared_target_ids)
        outcomes = tuple(schema.outcome_variant_ids)
    kind: HandleKind = "command" if descriptor.kind == "command" else "view"
    effect: EffectState
    if descriptor.effect in {"dynamic", "observed", "declared"}:
        effect = descriptor.effect
    else:
        effect = "dynamic"
    return CatalogEntry(
        logical_id=descriptor.logical_id,
        kind=kind,
        descriptor_version=descriptor.version,
        descriptor_fingerprint=descriptor_fingerprint(descriptor),
        effect_state=effect,
        type_schema_version=type_version,
        type_schema_fingerprint=type_fp,
        handler_fingerprint=handler_fp,
        model_fingerprint=model_fp,
        boundary_sources=boundary,
        field_paths=field_paths,
        control_dispositions=dispositions,
        sensitivity_flags=sensitivity,
        identity_flags=identity,
        declared_target_ids=declared,
        outcome_variant_ids=outcomes,
        provenance={"app_id": descriptor.app_id},
    )


@dataclass(frozen=True, slots=True)
class InteractionCatalog:
    schema_version: int = CATALOG_SCHEMA_VERSION
    app_id: str = ""
    entries: Mapping[str, CatalogEntry] = field(default_factory=_empty_entry_mapping)
    catalog_projections: Mapping[str, PackageProjection] = field(
        default_factory=_empty_projection_mapping
    )
    sealed: bool = False
    profile: RedactionProfile = "production"
    limitations: tuple[str, ...] = ()
    diagnostics: tuple[str, ...] = ()
    provenance: Mapping[str, JsonValue] = field(default_factory=_empty_json_object)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "entries",
            dict(sorted(self.entries.items(), key=lambda item: item[0])),
        )
        object.__setattr__(
            self,
            "catalog_projections",
            dict(sorted(self.catalog_projections.items(), key=lambda item: item[0])),
        )
        object.__setattr__(self, "provenance", dict(self.provenance))
        if len(self.entries) > MAX_CATALOG_ENTRIES:
            raise _catalog_error(
                HED_CATALOG_0005,
                title="Catalog entry limit exceeded",
                explanation=f"{len(self.entries)} entries exceeds {MAX_CATALOG_ENTRIES}.",
                remediation="Split applications rather than indexing unbounded handlers.",
            )
        if len(self.catalog_projections) > MAX_PROJECTIONS:
            raise _catalog_error(
                HED_CATALOG_0005,
                title="Catalog projection limit exceeded",
                explanation=(
                    f"{len(self.catalog_projections)} projections exceeds {MAX_PROJECTIONS}."
                ),
                remediation="Disable unused package providers.",
            )

    @property
    def fingerprint(self) -> str:
        payload = {
            "schema_version": self.schema_version,
            "app_id": self.app_id,
            "entries": {
                logical_id: entry.as_mapping(profile=self.profile)["fingerprint"]
                for logical_id, entry in self.entries.items()
            },
            "projections": {
                name: projection.as_mapping()["fingerprint"]
                for name, projection in self.catalog_projections.items()
            },
        }
        return catalog_fingerprint(payload)

    def get(self, logical_id: str) -> CatalogEntry | None:
        return self.entries.get(logical_id)

    def require(self, logical_id: str) -> CatalogEntry:
        entry = self.get(logical_id)
        if entry is None:
            raise _catalog_error(
                HED_CATALOG_0004,
                title="Catalog entry not found",
                explanation=f"No sealed catalog entry for {logical_id!r}.",
                remediation="Register the view/command before catalog lookup.",
            )
        return entry

    def views(self) -> tuple[CatalogEntry, ...]:
        return tuple(entry for entry in self.entries.values() if entry.kind == "view")

    def commands(self) -> tuple[CatalogEntry, ...]:
        return tuple(entry for entry in self.entries.values() if entry.kind == "command")

    def projections(self, namespace: str) -> tuple[PackageProjection, ...]:
        found: list[PackageProjection] = []
        catalog_level = self.catalog_projections.get(namespace)
        if catalog_level is not None:
            found.append(catalog_level)
        for entry in self.entries.values():
            item = entry.projections.get(namespace)
            if item is not None:
                found.append(item)
        return tuple(found)

    def to_manifest(self, *, profile: RedactionProfile = "production") -> InteractionManifest:
        entries = tuple(entry.as_mapping(profile=profile) for entry in self.entries.values())
        projections = tuple(item.as_mapping() for item in self.catalog_projections.values())
        diagnostics = list(self.diagnostics)
        if profile == "production":
            diagnostics = [item for item in diagnostics if "source" not in item.lower()]
        provenance = dict(self.provenance)
        if profile == "production":
            for key in ("source_path", "source", "file_path"):
                provenance.pop(key, None)
        body = cast(
            JsonObject,
            {
                "format_version": MANIFEST_FORMAT_VERSION,
                "profile": profile,
                "schema_version": self.schema_version,
                "app_id": self.app_id,
                "catalog_fingerprint": self.fingerprint,
                "entries": list(entries),
                "projections": list(projections),
                "diagnostics": diagnostics[:MAX_DIAGNOSTICS],
                "limitations": list(self.limitations),
                "provenance": provenance,
            },
        )
        _assert_bounds(body)
        encoded = canonical_json(body)
        if len(encoded.encode("utf-8")) > MAX_MANIFEST_BYTES:
            raise _catalog_error(
                HED_CATALOG_0005,
                title="Manifest exceeds byte bound",
                explanation=f"Serialized catalog exceeds {MAX_MANIFEST_BYTES} bytes.",
                remediation="Reduce entries, projections, or diagnostics.",
            )
        fingerprint = catalog_fingerprint(body)
        body["fingerprint"] = fingerprint
        _walk_forbidden(body, production=profile == "production")
        return InteractionManifest(
            format_version=MANIFEST_FORMAT_VERSION,
            profile=profile,
            app_id=self.app_id,
            catalog_fingerprint=self.fingerprint,
            fingerprint=fingerprint,
            entries=entries,
            projections=projections,
            diagnostics=tuple(diagnostics[:MAX_DIAGNOSTICS]),
            limitations=self.limitations,
            provenance=provenance,
            payload=body,
        )


@dataclass(frozen=True, slots=True)
class InteractionManifest:
    format_version: int = MANIFEST_FORMAT_VERSION
    profile: RedactionProfile = "production"
    app_id: str = ""
    catalog_fingerprint: str = ""
    fingerprint: str = ""
    entries: tuple[JsonObject, ...] = ()
    projections: tuple[JsonObject, ...] = ()
    diagnostics: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    provenance: Mapping[str, JsonValue] = field(default_factory=_empty_json_object)
    payload: Mapping[str, JsonValue] = field(default_factory=_empty_json_object)

    def __post_init__(self) -> None:
        object.__setattr__(self, "provenance", dict(self.provenance))
        object.__setattr__(self, "payload", dict(self.payload))

    def as_mapping(self) -> JsonObject:
        if self.payload:
            return dict(self.payload)
        body: JsonObject = {
            "format_version": self.format_version,
            "profile": self.profile,
            "app_id": self.app_id,
            "catalog_fingerprint": self.catalog_fingerprint,
            "entries": [dict(item) for item in self.entries],
            "projections": [dict(item) for item in self.projections],
            "diagnostics": list(self.diagnostics),
            "limitations": list(self.limitations),
            "provenance": dict(self.provenance),
        }
        body["fingerprint"] = self.fingerprint or catalog_fingerprint(body)
        return body

    def write_json(self, path: Path) -> None:
        write_json_atomic(Path(path), self.as_mapping())

    @classmethod
    def read_json(cls, path: Path) -> InteractionManifest:
        target = Path(path)
        if not target.is_file():
            raise _catalog_error(
                HED_CATALOG_0006,
                title="Interaction manifest missing",
                explanation=f"No interactions.json at {target}.",
                remediation=(
                    "Run `hedron build` (optionally with `--app`) to emit the sibling manifest."
                ),
            )
        raw = target.read_bytes()
        if len(raw) > MAX_MANIFEST_BYTES:
            raise _catalog_error(
                HED_CATALOG_0005,
                title="Interaction manifest too large",
                explanation=f"{target} exceeds {MAX_MANIFEST_BYTES} bytes.",
                remediation="Regenerate a bounded production manifest.",
            )
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise _catalog_error(
                HED_CATALOG_0007,
                title="Interaction manifest is not UTF-8",
                explanation=str(exc),
                remediation="Emit canonical UTF-8 JSON via `hedron build`.",
            ) from exc
        try:
            decoded: object = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
        except (json.JSONDecodeError, CatalogVersionError) as exc:
            if isinstance(exc, CatalogVersionError):
                raise
            raise _catalog_error(
                HED_CATALOG_0007,
                title="Interaction manifest is not valid JSON",
                explanation=str(exc),
                remediation="Regenerate interactions.json; truncated files fail closed.",
            ) from exc
        if not is_string_mapping(decoded):
            raise _catalog_error(
                HED_CATALOG_0007,
                title="Interaction manifest must be an object",
                explanation="Top-level JSON value was not an object.",
                remediation="Use the sealed catalog writer.",
            )
        # The standard JSON decoder and duplicate-key hook admit only
        # JsonValue members; the top-level guard establishes the object shape.
        data = cast(JsonObject, decoded)
        version = data.get("format_version")
        if version != MANIFEST_FORMAT_VERSION:
            raise _catalog_error(
                HED_CATALOG_0001,
                title="Unsupported interaction manifest version",
                explanation=f"format_version={version!r} is not {MANIFEST_FORMAT_VERSION}.",
                remediation="Regenerate the manifest with the current Hedron train.",
            )
        profile_value = data.get("profile", "production")
        if not isinstance(profile_value, str) or profile_value not in {
            "production",
            "development",
            "conformance",
        }:
            raise _catalog_error(
                HED_CATALOG_0001,
                title="Unknown redaction profile",
                explanation=f"profile={profile_value!r} is not a closed 0.45 profile.",
                remediation="Use production, development, or conformance.",
            )
        profile = cast(RedactionProfile, profile_value)
        _walk_forbidden(data, production=profile == "production")
        claimed = _manifest_string(data.get("fingerprint"), field_name="fingerprint")
        body = {key: value for key, value in data.items() if key != "fingerprint"}
        actual = catalog_fingerprint(body)
        if claimed and claimed != actual:
            raise _catalog_error(
                HED_CATALOG_0001,
                title="Interaction manifest fingerprint mismatch",
                explanation="Whole-document fingerprint does not match canonical JSON.",
                remediation="Do not edit interactions.json by hand; regenerate it.",
            )
        entries = _manifest_objects(data.get("entries", []), field_name="entries")
        projections = _manifest_objects(data.get("projections", []), field_name="projections")
        return cls(
            format_version=MANIFEST_FORMAT_VERSION,
            profile=profile,
            app_id=_manifest_string(data.get("app_id"), field_name="app_id"),
            catalog_fingerprint=_manifest_string(
                data.get("catalog_fingerprint"), field_name="catalog_fingerprint"
            ),
            fingerprint=actual,
            entries=entries,
            projections=projections,
            diagnostics=_manifest_strings(data.get("diagnostics", []), field_name="diagnostics"),
            limitations=_manifest_strings(data.get("limitations", []), field_name="limitations"),
            provenance=_as_object(data.get("provenance")),
            payload=data,
        )

    def validate_against(self, catalog: InteractionCatalog) -> None:
        if self.format_version != MANIFEST_FORMAT_VERSION:
            raise _catalog_error(
                HED_CATALOG_0001,
                title="Manifest version cannot validate this catalog",
                explanation="Reader/writer versions disagree.",
                remediation="Regenerate interactions.json.",
            )
        if self.app_id and catalog.app_id and self.app_id != catalog.app_id:
            raise _catalog_error(
                HED_CATALOG_0001,
                title="Cross-app catalog reuse refused",
                explanation=f"Manifest app_id {self.app_id!r} != live {catalog.app_id!r}.",
                remediation="Build and serve the same application catalog.",
            )
        if self.catalog_fingerprint and self.catalog_fingerprint != catalog.fingerprint:
            raise _catalog_error(
                HED_CATALOG_0001,
                title="Stale interaction catalog",
                explanation="Sealed catalog fingerprint does not match the build manifest.",
                remediation="Run `hedron build` against the same registered handlers.",
            )
        live_ids = set(catalog.entries)
        manifest_ids = {str(entry.get("logical_id")) for entry in self.entries}
        missing = sorted(live_ids - manifest_ids)
        extra = sorted(manifest_ids - live_ids)
        if missing or extra:
            raise _catalog_error(
                HED_CATALOG_0001,
                title="Catalog entry set mismatch",
                explanation=f"missing={missing} extra={extra}",
                remediation="Regenerate the production interactions.json.",
            )
        for entry in self.entries:
            logical_id = str(entry.get("logical_id") or "")
            live = catalog.require(logical_id)
            claimed = str(entry.get("descriptor_fingerprint") or "")
            if claimed != live.descriptor_fingerprint:
                raise _catalog_error(
                    HED_CATALOG_0001,
                    title="Descriptor fingerprint mismatch",
                    explanation=f"{logical_id} descriptor fingerprint is stale.",
                    remediation="Rebuild; catalog ids are not capabilities.",
                )
            claimed_type = entry.get("type_schema_fingerprint")
            if claimed_type not in {None, ""} and claimed_type != live.type_schema_fingerprint:
                raise _catalog_error(
                    HED_CATALOG_0001,
                    title="TypeSchema fingerprint mismatch",
                    explanation=f"{logical_id} type fingerprint is stale.",
                    remediation="Rebuild after type-authoring changes.",
                )


def _malformed_manifest(field_name: str, expected: str) -> CatalogVersionError:
    return _catalog_error(
        HED_CATALOG_0007,
        title="Malformed interaction manifest field",
        explanation=f"{field_name} must be {expected}.",
        remediation="Regenerate the sealed manifest.",
    )


def _manifest_string(value: object, *, field_name: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise _malformed_manifest(field_name, "a string")
    return value


def _manifest_strings(value: object, *, field_name: str) -> tuple[str, ...]:
    if not is_object_list(value):
        raise _malformed_manifest(field_name, "an array of strings")
    if not all(isinstance(item, str) for item in value):
        raise _malformed_manifest(field_name, "an array of strings")
    return tuple(item for item in value if isinstance(item, str))


def _manifest_objects(value: object, *, field_name: str) -> tuple[JsonObject, ...]:
    if not is_object_list(value):
        raise _malformed_manifest(field_name, "an array of objects")
    objects: list[JsonObject] = []
    for item in value:
        if not is_string_mapping(item):
            raise _malformed_manifest(field_name, "an array of objects")
        # The caller obtains these members from a validated standard-library
        # JSON decode, so every nested member already satisfies JsonValue.
        objects.append(cast(JsonObject, item))
    return tuple(objects)


def _reject_duplicate_keys(pairs: list[tuple[str, JsonValue]]) -> dict[str, JsonValue]:
    out: dict[str, JsonValue] = {}
    for key, value in pairs:
        if key in out:
            raise _catalog_error(
                HED_CATALOG_0007,
                title="Duplicate JSON keys refused",
                explanation=f"Key {key!r} appeared more than once.",
                remediation="Emit canonical JSON without duplicate keys.",
            )
        out[key] = value
    return out


def _as_object(value: object) -> JsonObject:
    if not isinstance(value, Mapping):
        return {}
    mapping = cast(Mapping[object, object], value)
    return {str(key): cast(JsonValue, item) for key, item in mapping.items()}


_LOCK = threading.RLock()
_PROVIDERS: dict[str, ProjectionProvider] = {}
_sealed = False
_sealed_catalog: InteractionCatalog | None = None
_scoped_catalog: ContextVar[InteractionCatalog | None] = ContextVar(
    "hedron_interaction_catalog", default=None
)
_catalog_scope_active: ContextVar[bool] = ContextVar("hedron_catalog_scope_active", default=False)
_scoped_providers: ContextVar[dict[str, ProjectionProvider] | None] = ContextVar(
    "hedron_projection_registry", default=None
)


def _active_providers() -> dict[str, ProjectionProvider]:
    scoped = _scoped_providers.get()
    return _PROVIDERS if scoped is None else scoped


def new_projection_registry() -> dict[str, ProjectionProvider]:
    """Create an application-owned provider registry seeded from compatibility state."""
    with _LOCK:
        return dict(_PROVIDERS)


@contextmanager
def use_projection_registry(
    providers: dict[str, ProjectionProvider],
) -> Generator[None, None, None]:
    """Bind projection providers to one application/task context."""
    token = _scoped_providers.set(providers)
    try:
        yield
    finally:
        _scoped_providers.reset(token)


def _catalog_is_sealed() -> bool:
    if _catalog_scope_active.get():
        return _scoped_catalog.get() is not None
    return _sealed


def register_projection_provider(provider: ProjectionProvider, *, plugin: str = "") -> None:
    del plugin
    with _LOCK:
        if _catalog_is_sealed():
            raise _catalog_error(
                HED_CATALOG_0003,
                title="Cannot register projections after catalog seal",
                explanation=f"Provider {getattr(provider, 'namespace', '?')!r} arrived too late.",
                remediation="Register providers during plugin start, before seal_registry().",
            )
        namespace = str(provider.namespace)
        if namespace in RESERVED_PROJECTION_NAMESPACES or not _NAMESPACE_RE.fullmatch(namespace):
            raise _catalog_error(
                HED_PROJECTION_0001,
                title="Invalid projection namespace",
                explanation=f"Namespace {namespace!r} cannot be registered.",
                remediation="Use reverse-DNS or a Hedron-reserved dotted namespace.",
            )
        providers = _active_providers()
        existing = providers.get(namespace)
        if existing is not None and existing is not provider:
            raise _catalog_error(
                HED_PROJECTION_0001,
                title="Duplicate projection namespace",
                explanation=(
                    f"Namespace {namespace!r} is owned by "
                    f"{getattr(existing, 'provider', existing)!r} "
                    f"and {getattr(provider, 'provider', provider)!r}."
                ),
                remediation="Disable one provider; namespaces do not merge.",
            )
        providers[namespace] = provider


def unregister_projection_provider(namespace: str) -> None:
    with _LOCK:
        if _catalog_is_sealed():
            raise _catalog_error(
                HED_PROJECTION_0006,
                title="Cannot uninstall projections after catalog seal",
                explanation=f"Namespace {namespace!r} is sealed with the catalog.",
                remediation="Disable the plugin before startup seal.",
            )
        _active_providers().pop(namespace, None)


def list_projection_providers() -> tuple[ProjectionProvider, ...]:
    with _LOCK:
        providers = _active_providers()
        return tuple(providers[name] for name in sorted(providers))


def snapshot_projection_providers() -> dict[str, ProjectionProvider]:
    with _LOCK:
        return dict(_active_providers())


def restore_projection_providers(snapshot: Mapping[str, ProjectionProvider]) -> None:
    with _LOCK:
        providers = _active_providers()
        providers.clear()
        providers.update(snapshot)


def get_sealed_catalog() -> InteractionCatalog | None:
    if _catalog_scope_active.get():
        return _scoped_catalog.get()
    return _sealed_catalog


@contextmanager
def use_catalog_context(
    catalog: InteractionCatalog | None = None,
) -> Generator[None, None, None]:
    """Create an application-local catalog scope for startup and requests."""
    active_token = _catalog_scope_active.set(True)
    catalog_token = _scoped_catalog.set(catalog)
    try:
        yield
    finally:
        _scoped_catalog.reset(catalog_token)
        _catalog_scope_active.reset(active_token)


def compile_interaction_catalog(
    *,
    app_id: str | None = None,
    profile: RedactionProfile = "production",
    trusted: bool = True,
    sealed: bool = False,
) -> InteractionCatalog:
    descriptors = list_handle_descriptors(app_id=app_id)
    seen: dict[str, BaseHandleDescriptor] = {}
    entries: dict[str, CatalogEntry] = {}
    for descriptor in descriptors:
        prior = seen.get(descriptor.logical_id)
        if prior is not None and (
            prior.app_id != descriptor.app_id
            or descriptor_fingerprint(prior) != descriptor_fingerprint(descriptor)
        ):
            raise _catalog_error(
                HED_CATALOG_0002,
                title="Duplicate catalog logical id",
                explanation=(
                    f"{descriptor.logical_id!r} is owned by {prior.app_id!r} and "
                    f"{descriptor.app_id!r}."
                ),
                remediation="Use distinct logical ids per app-owned handler.",
            )
        seen[descriptor.logical_id] = descriptor
        entries[descriptor.logical_id] = entry_from_descriptor(descriptor)
    draft = InteractionCatalog(
        app_id=app_id or "",
        entries=entries,
        profile=profile,
        provenance={"unknown": False},
    )
    attached_entries = dict(entries)
    catalog_projections: dict[str, PackageProjection] = {}
    diagnostics: list[str] = []
    for provider in list_projection_providers():
        if not trusted:
            diagnostics.append(f"skipped untrusted provider {provider.namespace}")
            continue
        try:
            projected = provider.project(
                tuple(attached_entries.values()),
                catalog_fingerprint=draft.fingerprint,
                trusted=trusted,
            )
        except CatalogVersionError:
            raise
        except Exception as exc:
            raise _catalog_error(
                HED_PROJECTION_0002,
                title="Projection provider failed",
                explanation=f"{provider.namespace}: {exc}",
                remediation="Fix the provider; the underlying interaction stays usable.",
            ) from exc
        if len(projected) > MAX_PROJECTIONS:
            raise _catalog_error(
                HED_PROJECTION_0002,
                title="Provider returned too many projections",
                explanation=f"{provider.namespace} exceeded {MAX_PROJECTIONS}.",
                remediation="Return one catalog-level or per-entry projection.",
            )
        for item in projected:
            if item.schema_version != PROJECTION_SCHEMA_VERSION:
                diagnostics.append(
                    f"unsupported projection version {item.namespace}={item.schema_version}"
                )
                continue
            if item.entry_fingerprint:
                matched = False
                next_entries: dict[str, CatalogEntry] = {}
                for logical_id, entry in attached_entries.items():
                    mapping = dict(entry.projections)
                    entry_fp = str(entry.as_mapping(profile=profile)["fingerprint"])
                    if entry_fp == item.entry_fingerprint:
                        if item.namespace in mapping:
                            raise _catalog_error(
                                HED_PROJECTION_0001,
                                title="Duplicate per-entry projection",
                                explanation=f"{item.namespace} already attached to {logical_id}.",
                                remediation="One namespace per entry.",
                            )
                        mapping[item.namespace] = item
                        matched = True
                    next_entries[logical_id] = replace(entry, projections=mapping)
                attached_entries = next_entries
                if not matched:
                    diagnostics.append(
                        f"stale entry fingerprint for {item.namespace}; underlying entry remains"
                    )
            else:
                if item.namespace in catalog_projections:
                    raise _catalog_error(
                        HED_PROJECTION_0001,
                        title="Duplicate catalog projection",
                        explanation=f"Namespace {item.namespace} already has a catalog projection.",
                        remediation="Disable one provider.",
                    )
                catalog_projections[item.namespace] = item
    return InteractionCatalog(
        app_id=app_id or "",
        entries=attached_entries,
        catalog_projections=catalog_projections,
        sealed=sealed,
        profile=profile,
        diagnostics=tuple(diagnostics[:MAX_DIAGNOSTICS]),
        provenance={"unknown": False, "app_id": app_id or ""},
    )


def seal_interaction_catalog(
    *,
    app_id: str | None = None,
    profile: RedactionProfile = "production",
) -> InteractionCatalog:
    scoped = _scoped_catalog.get()
    if _catalog_scope_active.get():
        if scoped is None:
            scoped = compile_interaction_catalog(app_id=app_id, profile=profile, sealed=True)
            _scoped_catalog.set(scoped)
            return scoped
        if app_id and scoped.app_id and scoped.app_id != app_id:
            raise _catalog_error(
                HED_CATALOG_0001,
                title="Catalog already sealed for another app",
                explanation=f"Sealed {scoped.app_id!r}; requested {app_id!r}.",
                remediation="Use the application-owned catalog context.",
            )
        return scoped
    global _sealed, _sealed_catalog
    with _LOCK:
        if _sealed and _sealed_catalog is not None:
            if app_id and _sealed_catalog.app_id and _sealed_catalog.app_id != app_id:
                raise _catalog_error(
                    HED_CATALOG_0001,
                    title="Catalog already sealed for another app",
                    explanation=f"Sealed {_sealed_catalog.app_id!r}; requested {app_id!r}.",
                    remediation="Reset catalog state between apps in tests.",
                )
            return _sealed_catalog
        catalog = compile_interaction_catalog(app_id=app_id, profile=profile, sealed=True)
        _sealed_catalog = catalog
        _sealed = True
        return catalog


def reset_catalog_for_tests() -> None:
    global _sealed, _sealed_catalog
    with _LOCK:
        _PROVIDERS.clear()
        _sealed = False
        _sealed_catalog = None
