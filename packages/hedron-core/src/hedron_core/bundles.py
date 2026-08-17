"""Immutable FeatureBundle values and atomic process-local inclusion (phase 0.46).

Host-neutral. Bundles register ordinary 0.43–0.45 artifacts; they are not
executors and not FeatureManifest. Handle materialization stays on the host.
"""

from __future__ import annotations

import threading
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal, Protocol, runtime_checkable

from hedron_core.catalog import (
    PackageProjection,
    get_sealed_catalog,
    register_projection_provider,
    unregister_projection_provider,
)
from hedron_core.codes import (
    HED_BUNDLE_0001,
    HED_BUNDLE_0002,
    HED_BUNDLE_0003,
    HED_BUNDLE_0004,
    HED_BUNDLE_0005,
    HED_BUNDLE_0006,
    HED_BUNDLE_0007,
    HED_BUNDLE_0009,
    HED_BUNDLE_0010,
)
from hedron_core.diagnostics import DiagnosticSeverity, HedronError, make_diagnostic
from hedron_core.updates import list_handle_descriptors, unregister_handle_descriptor

MAX_BUNDLES = 512
MAX_BUNDLE_DEPENDENCY_DEPTH = 16
MAX_GENERATED_SCENARIOS_PER_BUNDLE = 128
MAX_WORKSPACE_FIELDS = 256
MAX_CHART_SELECTION_ITEMS = 1000
MAX_EFFECT_FANOUT = 32

_LOGICAL_RE_PREFIX = "abcdefghijklmnopqrstuvwxyz"

__all__ = [
    "MAX_BUNDLES",
    "MAX_BUNDLE_DEPENDENCY_DEPTH",
    "MAX_CHART_SELECTION_ITEMS",
    "MAX_EFFECT_FANOUT",
    "MAX_GENERATED_SCENARIOS_PER_BUNDLE",
    "MAX_WORKSPACE_FIELDS",
    "FeatureBundle",
    "FeatureConflictError",
    "FeatureProvider",
    "FeatureRequirement",
    "eject_bundle",
    "eject_source",
    "include_bundle",
    "included_bundles",
    "reset_bundles_for_tests",
    "resolve_feature",
]


class FeatureConflictError(HedronError):
    """Atomic FeatureBundle inclusion failure; no partial artifacts remain."""


@runtime_checkable
class FeatureProvider(Protocol):
    """Package configuration that compiles to an immutable FeatureBundle."""

    def to_bundle(self) -> FeatureBundle: ...


@dataclass(frozen=True, slots=True)
class FeatureRequirement:
    """Declared package/host/browser capability required or optional for a bundle."""

    name: str
    required: bool = True
    kind: Literal["package", "host", "browser", "capability"] = "package"


@dataclass(frozen=True, slots=True)
class FeatureBundle:
    """Immutable package feature registration description; no execution semantics."""

    logical_id: str
    provider: str
    provider_version: str
    views: tuple[object, ...] = ()
    commands: tuple[object, ...] = ()
    components: tuple[object, ...] = ()
    scenarios: tuple[object, ...] = ()
    projections: tuple[PackageProjection, ...] = ()
    requirements: tuple[FeatureRequirement, ...] = ()
    dependencies: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    optional_capabilities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not str(self.logical_id).strip() or not str(self.provider).strip():
            raise _bundle_error(
                HED_BUNDLE_0007,
                title="Invalid FeatureBundle identity",
                explanation="logical_id and provider are required.",
                remediation="Give the bundle a stable package-namespaced id and provider.",
            )
        if len(self.scenarios) > MAX_GENERATED_SCENARIOS_PER_BUNDLE:
            raise _bundle_error(
                HED_BUNDLE_0005,
                title="Generated scenario bound exceeded",
                explanation=(
                    f"Bundle {self.logical_id!r} has {len(self.scenarios)} scenarios; "
                    f"max is {MAX_GENERATED_SCENARIOS_PER_BUNDLE}."
                ),
                remediation="Ship AppScenario fixtures only; drop generated extras.",
            )


def _bundle_error(
    code: str,
    *,
    title: str,
    explanation: str,
    remediation: str,
) -> FeatureConflictError:
    return FeatureConflictError(
        make_diagnostic(
            code,
            severity=DiagnosticSeverity.ERROR,
            title=title,
            explanation=explanation,
            remediation=remediation,
        )
    )


_LOCK = threading.RLock()
_BUNDLES: dict[tuple[str, str], FeatureBundle] = {}
_PROJECTION_NAMESPACES: dict[tuple[str, str], tuple[str, ...]] = {}


def resolve_feature(feature: FeatureBundle | FeatureProvider) -> FeatureBundle:
    if isinstance(feature, FeatureBundle):
        return feature
    to_bundle = getattr(feature, "to_bundle", None)
    if not callable(to_bundle):
        raise _bundle_error(
            HED_BUNDLE_0007,
            title="Not a FeatureBundle or FeatureProvider",
            explanation=f"{type(feature).__name__} cannot compile to a FeatureBundle.",
            remediation="Pass FeatureBundle or a provider with to_bundle().",
        )
    bundle = to_bundle()
    if not isinstance(bundle, FeatureBundle):
        raise _bundle_error(
            HED_BUNDLE_0007,
            title="FeatureProvider returned a non-bundle",
            explanation=f"{type(feature).__name__}.to_bundle() returned {type(bundle).__name__}.",
            remediation="to_bundle() must return an immutable FeatureBundle.",
        )
    return bundle


def _sealed() -> bool:
    return get_sealed_catalog() is not None


def included_bundles(*, app_id: str | None = None) -> tuple[FeatureBundle, ...]:
    with _LOCK:
        rows = (
            list(_BUNDLES.values())
            if app_id is None
            else [b for (aid, _), b in _BUNDLES.items() if aid == app_id]
        )
        return tuple(sorted(rows, key=lambda item: item.logical_id))


def _depth(
    logical_id: str, graph: Mapping[str, Sequence[str]], *, seeing: tuple[str, ...] = ()
) -> int:
    if logical_id in seeing:
        raise _bundle_error(
            HED_BUNDLE_0003,
            title="FeatureBundle dependency cycle",
            explanation=f"Cycle involving {logical_id!r}: {seeing + (logical_id,)}.",
            remediation="Declare an acyclic dependency graph.",
        )
    deps = graph.get(logical_id, ())
    if not deps:
        return 1
    return 1 + max(_depth(dep, graph, seeing=seeing + (logical_id,)) for dep in deps)


def include_bundle(
    bundle: FeatureBundle,
    *,
    app_id: str,
    capabilities: Mapping[str, bool] | None = None,
    known_logical_ids: Sequence[str] | None = None,
    allow_privileged: bool = True,
) -> FeatureBundle:
    """Validate then record a bundle. Hosts materialize handles before calling this."""
    if _sealed():
        raise _bundle_error(
            HED_BUNDLE_0001,
            title="Cannot include FeatureBundle after catalog seal",
            explanation=f"Bundle {bundle.logical_id!r} arrived after seal_app_catalog.",
            remediation="Call include_feature in the same window as include_component.",
        )
    caps = dict(capabilities or {})
    caps.setdefault(bundle.provider, True)
    with _LOCK:
        if len(_BUNDLES) >= MAX_BUNDLES:
            raise _bundle_error(
                HED_BUNDLE_0005,
                title="FeatureBundle count bound exceeded",
                explanation=f"At most {MAX_BUNDLES} bundles may be included.",
                remediation="Eject unused bundles or split applications.",
            )
        slot = (app_id, bundle.logical_id)
        if slot in _BUNDLES:
            existing = _BUNDLES[slot]
            if existing == bundle:
                return existing
            raise _bundle_error(
                HED_BUNDLE_0002,
                title="Duplicate FeatureBundle id",
                explanation=f"Bundle {bundle.logical_id!r} is already included on this app.",
                remediation="Use a distinct logical_id or eject the existing bundle.",
            )
        existing_graph = {
            item.logical_id: item.dependencies for item in included_bundles(app_id=app_id)
        }
        existing_graph[bundle.logical_id] = bundle.dependencies
        for dep in bundle.dependencies:
            if dep not in existing_graph or dep == bundle.logical_id:
                raise _bundle_error(
                    HED_BUNDLE_0003,
                    title="Missing FeatureBundle dependency",
                    explanation=(
                        f"Bundle {bundle.logical_id!r} depends on {dep!r}, which is not included."
                    ),
                    remediation="Include dependencies first in deterministic order.",
                )
        depth = _depth(bundle.logical_id, existing_graph)
        if depth > MAX_BUNDLE_DEPENDENCY_DEPTH:
            raise _bundle_error(
                HED_BUNDLE_0003,
                title="FeatureBundle dependency depth exceeded",
                explanation=f"Depth {depth} exceeds {MAX_BUNDLE_DEPENDENCY_DEPTH}.",
                remediation="Flatten declared bundle dependencies.",
            )
        for req in bundle.requirements:
            present = caps.get(req.name, False)
            if req.required and not present:
                raise _bundle_error(
                    HED_BUNDLE_0004,
                    title="Required FeatureBundle capability missing",
                    explanation=f"Bundle {bundle.logical_id!r} requires {req.name!r}.",
                    remediation="Install the package or satisfy the host/browser capability.",
                )
        if not allow_privileged and any(
            ident.startswith("hedron:")
            for ident in (bundle.logical_id,)
            if ident.startswith("hedron:") and bundle.provider not in {"hedron", "hedron-core"}
        ):
            raise _bundle_error(
                HED_BUNDLE_0010,
                title="Third-party bundle cannot use a privileged namespace",
                explanation=f"Provider {bundle.provider!r} cannot own {bundle.logical_id!r}.",
                remediation="Use a reverse-DNS id under the third-party package namespace.",
            )
        known = set(known_logical_ids or ())
        known.update(descriptor.logical_id for descriptor in list_handle_descriptors(app_id=app_id))
        claimed: list[str] = []
        for item in (*bundle.views, *bundle.commands):
            logical = getattr(item, "logical_id", None)
            if isinstance(logical, str) and logical:
                if logical in claimed:
                    raise _bundle_error(
                        HED_BUNDLE_0002,
                        title="Duplicate handle inside FeatureBundle",
                        explanation=f"Handle {logical!r} is listed twice in {bundle.logical_id!r}.",
                        remediation="Give each view/command a unique logical id.",
                    )
                claimed.append(logical)
        snapshot_ids = tuple(_BUNDLES)
        try:
            _BUNDLES[slot] = bundle
            registered: list[str] = []
            for projection in bundle.projections:
                namespace = projection.namespace

                class _Provider:
                    def __init__(self, proj: PackageProjection) -> None:
                        self.namespace = proj.namespace
                        self.provider = proj.provider
                        self._proj = proj

                    def project(
                        self,
                        entries: Sequence[object],
                        *,
                        catalog_fingerprint: str,
                        trusted: bool = True,
                    ) -> tuple[PackageProjection, ...]:
                        del entries, trusted
                        return (
                            PackageProjection(
                                namespace=self._proj.namespace,
                                schema_version=self._proj.schema_version,
                                provider=self._proj.provider or bundle.provider,
                                provider_version=self._proj.provider_version
                                or bundle.provider_version,
                                catalog_fingerprint=catalog_fingerprint
                                or self._proj.catalog_fingerprint,
                                entry_fingerprint=self._proj.entry_fingerprint,
                                capabilities=self._proj.capabilities,
                                data=dict(self._proj.data),
                                limitations=self._proj.limitations or bundle.limitations,
                                disposition=self._proj.disposition,
                            ),
                        )

                register_projection_provider(_Provider(projection), plugin=bundle.provider)
                registered.append(namespace)
            _PROJECTION_NAMESPACES[slot] = tuple(registered)
        except Exception as exc:
            _BUNDLES.pop(slot, None)
            for namespace in _PROJECTION_NAMESPACES.pop(slot, ()):
                unregister_projection_provider(namespace)
            extra = str(exc)
            raise _bundle_error(
                HED_BUNDLE_0006,
                title="FeatureBundle include rolled back",
                explanation=f"Including {bundle.logical_id!r} failed: {extra}",
                remediation="Fix the conflict and include again; no partial artifacts remain.",
            ) from exc
        if len(_BUNDLES) > MAX_BUNDLES:
            eject_bundle(bundle.logical_id, app_id=app_id)
            raise _bundle_error(
                HED_BUNDLE_0005,
                title="FeatureBundle count bound exceeded",
                explanation=f"At most {MAX_BUNDLES} bundles may be included.",
                remediation="Eject unused bundles or split applications.",
            )
        del snapshot_ids
        return bundle


def eject_bundle(logical_id: str, *, app_id: str) -> FeatureBundle:
    if _sealed():
        raise _bundle_error(
            HED_BUNDLE_0009,
            title="Cannot eject FeatureBundle after catalog seal",
            explanation=f"Bundle {logical_id!r} is sealed with the catalog.",
            remediation="Rebuild without the bundle, or eject before lifespan seal.",
        )
    slot = (app_id, logical_id)
    with _LOCK:
        bundle = _BUNDLES.pop(slot, None)
        if bundle is None:
            raise _bundle_error(
                HED_BUNDLE_0009,
                title="Unknown FeatureBundle",
                explanation=f"Bundle {logical_id!r} is not included on this app.",
                remediation="Inspect included bundles before eject.",
            )
        dependents = [
            item.logical_id
            for item in included_bundles(app_id=app_id)
            if logical_id in item.dependencies
        ]
        if dependents:
            _BUNDLES[slot] = bundle
            raise _bundle_error(
                HED_BUNDLE_0003,
                title="Cannot eject a required FeatureBundle dependency",
                explanation=f"{logical_id!r} is required by {dependents}.",
                remediation="Eject dependents first.",
            )
        for namespace in _PROJECTION_NAMESPACES.pop(slot, ()):
            unregister_projection_provider(namespace)
        for item in (*bundle.views, *bundle.commands):
            ident = getattr(item, "logical_id", None)
            if isinstance(ident, str) and ident:
                unregister_handle_descriptor(ident, app_id=app_id)
        return bundle


def eject_source(bundle: FeatureBundle) -> str:
    """Reviewable explicit-registration Python equivalent; never writes secrets."""
    view_ids = [
        getattr(item, "logical_id", None) or getattr(item, "__name__", repr(item))
        for item in bundle.views
    ]
    command_ids = [
        getattr(item, "logical_id", None) or getattr(item, "__name__", repr(item))
        for item in bundle.commands
    ]
    lines = [
        (
            f"# Ejected FeatureBundle {bundle.logical_id!r} from "
            f"{bundle.provider} {bundle.provider_version}"
        ),
        "# Register these ordinary handles instead of app.include_feature(...).",
        f"# Views: {', '.join(str(item) for item in view_ids) or '(none)'}",
        f"# Commands: {', '.join(str(item) for item in command_ids) or '(none)'}",
        f"# Projections: {', '.join(item.namespace for item in bundle.projections) or '(none)'}",
        "# This file is reviewable source, not a serialized workflow executor.",
        "",
    ]
    return "\n".join(lines)


def reset_bundles_for_tests() -> None:
    with _LOCK:
        _BUNDLES.clear()
        _PROJECTION_NAMESPACES.clear()


def snapshot_bundles() -> tuple[
    dict[tuple[str, str], FeatureBundle], dict[tuple[str, str], tuple[str, ...]]
]:
    with _LOCK:
        return dict(_BUNDLES), dict(_PROJECTION_NAMESPACES)


def restore_bundles(
    bundles: Mapping[tuple[str, str], FeatureBundle],
    namespaces: Mapping[tuple[str, str], tuple[str, ...]],
) -> None:
    with _LOCK:
        _BUNDLES.clear()
        _BUNDLES.update(bundles)
        _PROJECTION_NAMESPACES.clear()
        _PROJECTION_NAMESPACES.update(namespaces)
