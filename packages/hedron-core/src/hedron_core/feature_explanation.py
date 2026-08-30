"""Frozen feature explanation and source-map values (phase 0.58).

Schemas: ``hedron.feature-explanation/1``, ``hedron.feature-source-map/1``.
Callables appear only as ``module.qualname`` strings; callbacks are never invoked.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Final, Literal, cast

from hedron_core.bundles import (
    FeatureBundle,
    FeatureConflictError,
    FeatureProvider,
    resolve_feature,
)
from hedron_core.codes import HED_FEATURE_0001
from hedron_core.diagnostics import DiagnosticSeverity, make_diagnostic
from hedron_core.typing_aliases import JsonValue

__all__ = [
    "EXPLANATION_SCHEMA",
    "SOURCE_MAP_SCHEMA",
    "FeatureExplanation",
    "FeatureSourceMap",
    "callable_ref",
    "explain_feature",
    "source_map_for",
]

EXPLANATION_SCHEMA: Final = "hedron.feature-explanation/1"
SOURCE_MAP_SCHEMA: Final = "hedron.feature-source-map/1"


def callable_ref(value: object) -> str | None:
    """Return ``module.qualname`` for a callable; never invoke it."""
    if value is None or isinstance(value, type):
        # Types are allowed as metadata; prefer module.qualname when present.
        module = getattr(value, "__module__", None)
        qualname = getattr(value, "__qualname__", None)
        if isinstance(module, str) and isinstance(qualname, str) and module and qualname:
            return f"{module}.{qualname}"
        return None
    if not callable(value):
        return None
    module = getattr(value, "__module__", None)
    qualname = getattr(value, "__qualname__", None)
    if isinstance(module, str) and isinstance(qualname, str) and module and qualname:
        return f"{module}.{qualname}"
    name = getattr(value, "__name__", None)
    if isinstance(name, str) and name:
        return name
    return None


def _digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":")).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()


def _json_plan_value(value: object, *, field_name: str) -> JsonValue:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [_json_plan_value(item, field_name=field_name) for item in cast(list[object], value)]
    if isinstance(value, Mapping):
        mapping = cast(Mapping[object, object], value)
        if any(not isinstance(key, str) for key in mapping):
            raise ValueError(f"feature explanation field {field_name!r} has non-string keys")
        return {
            cast(str, key): _json_plan_value(item, field_name=field_name)
            for key, item in mapping.items()
        }
    raise ValueError(f"feature explanation field {field_name!r} is not JSON-compatible")


def _json_plan_list(plan: Mapping[str, object], field_name: str) -> list[JsonValue]:
    value = _json_plan_value(plan[field_name], field_name=field_name)
    if not isinstance(value, list):
        raise ValueError(f"feature explanation field {field_name!r} must be an array")
    return value


def _json_plan_object(plan: Mapping[str, object], field_name: str) -> dict[str, JsonValue]:
    value = _json_plan_value(plan[field_name], field_name=field_name)
    if not isinstance(value, dict):
        raise ValueError(f"feature explanation field {field_name!r} must be an object")
    return value


def _surface_entry(
    name: str,
    *,
    kind: str,
    route: str | None = None,
    handle_id: str | None = None,
) -> dict[str, JsonValue]:
    entry: dict[str, JsonValue] = {"name": name, "kind": kind}
    if route is not None:
        entry["route"] = route
    if handle_id is not None:
        entry["handle_id"] = handle_id
    return entry


def _surfaces_from_bundle(bundle: FeatureBundle) -> list[dict[str, JsonValue]]:
    declared: list[dict[str, JsonValue]] = []
    for projection in bundle.projections:
        data = projection.data
        raw = data.get("surfaces")
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, str) and item:
                    declared.append(_surface_entry(item, kind="declared"))
                elif isinstance(item, dict):
                    name = item.get("name")
                    if isinstance(name, str) and name:
                        kind = item.get("kind")
                        declared.append(
                            _surface_entry(
                                name,
                                kind=str(kind) if kind is not None else "declared",
                                route=str(item["route"]) if "route" in item else None,
                                handle_id=str(item["handle_id"]) if "handle_id" in item else None,
                            )
                        )
    if declared:
        return declared
    out: list[dict[str, JsonValue]] = []
    for item in bundle.views:
        ident = getattr(item, "logical_id", None) or getattr(item, "__name__", None)
        path = getattr(item, "path", None)
        out.append(
            _surface_entry(
                str(ident) if ident is not None else "view",
                kind="view",
                route=str(path) if path is not None else None,
                handle_id=str(ident) if ident is not None else None,
            )
        )
    for item in bundle.commands:
        ident = getattr(item, "logical_id", None) or getattr(item, "__name__", None)
        path = getattr(item, "path", None)
        out.append(
            _surface_entry(
                str(ident) if ident is not None else "command",
                kind="command",
                route=str(path) if path is not None else None,
                handle_id=str(ident) if ident is not None else None,
            )
        )
    return out


def _routes_from_bundle(bundle: FeatureBundle) -> list[dict[str, JsonValue]]:
    routes: list[dict[str, JsonValue]] = []
    for item in (*bundle.views, *bundle.commands):
        path = getattr(item, "path", None)
        ident = getattr(item, "logical_id", None) or getattr(item, "__name__", None)
        if path is None and ident is None:
            continue
        routes.append(
            {
                "path": str(path) if path is not None else "",
                "logical_id": str(ident) if ident is not None else "",
            }
        )
    return routes


def _security_from_bundle(bundle: FeatureBundle) -> dict[str, JsonValue]:
    reqs: list[JsonValue] = [
        {"name": item.name, "required": item.required, "kind": item.kind}
        for item in bundle.requirements
    ]
    return {
        "requirements": reqs,
        "optional_capabilities": list(bundle.optional_capabilities),
        "redacted": True,
    }


def _source_from_bundle(bundle: FeatureBundle) -> dict[str, JsonValue]:
    return {
        "provider": bundle.provider,
        "provider_version": bundle.provider_version,
        "dependencies": list(bundle.dependencies),
        "projections": [item.namespace for item in bundle.projections],
    }


def _effects_from_bundle(bundle: FeatureBundle) -> list[dict[str, JsonValue]]:
    effects: list[dict[str, JsonValue]] = []
    for item in (*bundle.views, *bundle.commands):
        declared = getattr(item, "__hedron_effects__", None)
        if declared is None:
            continue
        effects.append(
            {
                "handle": str(
                    getattr(item, "logical_id", None) or getattr(item, "__name__", "handle")
                ),
                "effects": str(type(declared).__name__),
            }
        )
    return effects


@dataclass(frozen=True, slots=True)
class FeatureExplanation:
    """Immutable redacted explanation value (``hedron.feature-explanation/1``)."""

    logical_id: str
    kind: str
    surfaces: tuple[Mapping[str, JsonValue], ...] = ()
    routes: tuple[Mapping[str, JsonValue], ...] = ()
    effects: tuple[Mapping[str, JsonValue], ...] = ()
    security: Mapping[str, JsonValue] = field(default_factory=dict[str, JsonValue])
    limitations: tuple[str, ...] = ()
    source: Mapping[str, JsonValue] = field(default_factory=dict[str, JsonValue])
    schema: Literal["hedron.feature-explanation/1"] = EXPLANATION_SCHEMA

    def to_mapping(self) -> dict[str, JsonValue]:
        return {
            "schema": self.schema,
            "logical_id": self.logical_id,
            "kind": self.kind,
            "surfaces": [dict(item) for item in self.surfaces],
            "routes": [dict(item) for item in self.routes],
            "effects": [dict(item) for item in self.effects],
            "security": dict(self.security),
            "limitations": list(self.limitations),
            "source": dict(self.source),
        }


@dataclass(frozen=True, slots=True)
class FeatureSourceMap:
    """Immutable ejection source map (``hedron.feature-source-map/1``)."""

    feature_id: str
    selection: str
    files: tuple[str, ...]
    facade_digest: str
    catalog_digest: str
    scenario_digest: str
    schema: Literal["hedron.feature-source-map/1"] = SOURCE_MAP_SCHEMA

    def to_mapping(self) -> dict[str, JsonValue]:
        return {
            "schema": self.schema,
            "feature_id": self.feature_id,
            "selection": self.selection,
            "files": list(self.files),
            "facade_digest": self.facade_digest,
            "catalog_digest": self.catalog_digest,
            "scenario_digest": self.scenario_digest,
        }


def explain_feature(
    bundle_or_plan: FeatureBundle | FeatureProvider | Mapping[str, object],
) -> Mapping[str, JsonValue]:
    """Build a frozen explanation mapping without invoking application callbacks.

    Accepts an included ``FeatureBundle``, a ``FeatureProvider`` (``to_bundle()`` only
    builds factories), or a precomputed plan mapping.
    """
    if isinstance(bundle_or_plan, Mapping):
        plan = dict(bundle_or_plan)
        schema = plan.get("schema", EXPLANATION_SCHEMA)
        if schema != EXPLANATION_SCHEMA:
            raise FeatureConflictError(
                make_diagnostic(
                    HED_FEATURE_0001,
                    severity=DiagnosticSeverity.ERROR,
                    title="Unsupported feature explanation schema",
                    explanation=f"Got schema={schema!r}; expected {EXPLANATION_SCHEMA!r}.",
                    remediation="Use hedron.feature-explanation/1 values only.",
                )
            )
        for key in (
            "logical_id",
            "kind",
            "surfaces",
            "routes",
            "effects",
            "security",
            "limitations",
            "source",
        ):
            if key not in plan:
                raise FeatureConflictError(
                    make_diagnostic(
                        HED_FEATURE_0001,
                        severity=DiagnosticSeverity.ERROR,
                        title="Incomplete feature explanation",
                        explanation=f"Missing required field {key!r}.",
                        remediation="Supply all hedron.feature-explanation/1 fields.",
                    )
                )
        return {
            "schema": EXPLANATION_SCHEMA,
            "logical_id": str(plan["logical_id"]),
            "kind": str(plan["kind"]),
            "surfaces": _json_plan_list(plan, "surfaces"),
            "routes": _json_plan_list(plan, "routes"),
            "effects": _json_plan_list(plan, "effects"),
            "security": _json_plan_object(plan, "security"),
            "limitations": _json_plan_list(plan, "limitations"),
            "source": _json_plan_object(plan, "source"),
        }

    bundle = resolve_feature(bundle_or_plan)
    kind = "FeatureBundle"
    provider_cls = type(bundle_or_plan)
    if not isinstance(bundle_or_plan, FeatureBundle):
        kind = provider_cls.__name__
    explanation = FeatureExplanation(
        logical_id=bundle.logical_id,
        kind=kind,
        surfaces=tuple(_surfaces_from_bundle(bundle)),
        routes=tuple(_routes_from_bundle(bundle)),
        effects=tuple(_effects_from_bundle(bundle)),
        security=_security_from_bundle(bundle),
        limitations=tuple(bundle.limitations),
        source=_source_from_bundle(bundle),
    )
    return explanation.to_mapping()


def source_map_for(
    *,
    feature_id: str,
    selection: str,
    files: Sequence[str],
    facade_source: str,
    catalog_payload: object = (),
    scenario_payload: object = (),
) -> FeatureSourceMap:
    """Build a project-relative source map for ejected feature output."""
    return FeatureSourceMap(
        feature_id=feature_id,
        selection=selection,
        files=tuple(files),
        facade_digest=_digest(facade_source),
        catalog_digest=_digest(catalog_payload),
        scenario_digest=_digest(scenario_payload),
    )
