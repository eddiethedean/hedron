"""Dependency-ordered application asset plans (ASSET-053).

Page emission honors placement / depends_on via :func:`ordered_registry_assets`
and :func:`compile_application_asset_plan`. Live registry ``AssetMeta`` is the
inject path for ordered scripts; build ``AssetEntry`` manifests remain
fingerprint/content metadata (placement/depends_on live on the registry).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from hedron_core.codes import (
    HED_ASSET_0531,
    HED_ASSET_0532,
    HED_ASSET_0533,
    HED_ASSET_0534,
    HED_ASSET_0535,
    HED_ASSET_0536,
    HED_ASSET_0537,
    HED_ASSET_0538,
)
from hedron_core.diagnostics import Diagnostic, DiagnosticSeverity, make_diagnostic
from hedron_core.rendering import AssetRef

__all__ = [
    "VALID_APPLICATION_ASSET_KINDS",
    "VALID_APPLICATION_ASSET_PLACEMENTS",
    "ApplicationAssetPlan",
    "ApplicationAssetSpec",
    "application_spec_to_asset_ref",
    "compile_application_asset_plan",
    "emit_safe_application_assets",
    "is_remote_application_href",
    "ordered_registry_assets",
    "specs_from_asset_refs",
]

VALID_APPLICATION_ASSET_KINDS = frozenset({"css", "js", "module"})
VALID_APPLICATION_ASSET_PLACEMENTS = frozenset({"head", "after_htmx_core", "body_end"})

_INTEGRITY_PREFIXES = ("sha256-", "sha384-", "sha512-")


@dataclass(frozen=True, slots=True)
class ApplicationAssetSpec:
    """One local CSS/JS/module asset in an application plan."""

    logical_id: str
    kind: str
    href: str
    depends_on: tuple[str, ...] = ()
    placement: str = "head"
    integrity: str | None = None

    @property
    def path(self) -> str:
        """Alias for ``href`` (registry-style naming)."""
        return self.href


@dataclass(frozen=True, slots=True)
class ApplicationAssetPlan:
    """Topo-sorted application assets with fail-closed diagnostics."""

    assets: tuple[ApplicationAssetSpec, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()
    ok: bool = True


def application_spec_to_asset_ref(spec: ApplicationAssetSpec) -> AssetRef:
    """Convert a compiled plan entry into an :class:`AssetRef` for inject."""
    attrs: dict[str, str] = {}
    if spec.integrity:
        attrs["integrity"] = spec.integrity
        attrs.setdefault("crossorigin", "anonymous")
    return AssetRef(
        kind=spec.kind,
        href=spec.href,
        attributes=MappingProxyType(attrs),
    )


def ordered_registry_assets() -> tuple[ApplicationAssetSpec, ...]:
    """Return dependency-ordered specs from the live asset registry.

    Used by :func:`~hedron_core.page_assets.inject_page_assets` so
    ``AssetMeta.depends_on`` / ``placement`` are honored at emit time.
    Returns ``()`` when the registry is empty. Specs that fail compile
    validation (missing deps, cycles, invalid SRI, remotes) are omitted.
    """
    from hedron_core.registry import get_registry

    specs: list[ApplicationAssetSpec] = []
    for meta in get_registry().assets():
        if meta.kind not in VALID_APPLICATION_ASSET_KINDS:
            continue
        integrity = meta.attributes.get("integrity")
        if integrity is None and meta.digest.startswith(_INTEGRITY_PREFIXES):
            integrity = meta.digest
        specs.append(
            ApplicationAssetSpec(
                logical_id=meta.logical_id,
                kind=meta.kind,
                href=meta.path,
                depends_on=meta.depends_on,
                placement=meta.placement,
                integrity=integrity,
            )
        )
    if not specs:
        return ()
    plan = compile_application_asset_plan(specs)
    return emit_safe_application_assets(plan, fallback=())


def _error_logical_ids(diagnostics: Sequence[Diagnostic]) -> frozenset[str]:
    bad: set[str] = set()
    for diag in diagnostics:
        if diag.severity is not DiagnosticSeverity.ERROR:
            continue
        ctx = diag.context or {}
        logical_id = ctx.get("logical_id")
        if isinstance(logical_id, str) and logical_id:
            bad.add(logical_id)
    return frozenset(bad)


def emit_safe_application_assets(
    plan: ApplicationAssetPlan,
    *,
    fallback: tuple[ApplicationAssetSpec, ...] = (),
) -> tuple[ApplicationAssetSpec, ...]:
    """Return only assets safe to emit (drop ERROR-linked / invalid SRI specs)."""
    candidates = plan.assets if plan.assets else fallback
    if not candidates:
        return ()
    bad = _error_logical_ids(plan.diagnostics)
    out: list[ApplicationAssetSpec] = []
    for spec in candidates:
        if spec.logical_id in bad:
            continue
        if spec.integrity is not None and not _valid_integrity(spec.integrity):
            continue
        if spec.kind not in VALID_APPLICATION_ASSET_KINDS:
            continue
        if spec.placement not in VALID_APPLICATION_ASSET_PLACEMENTS:
            continue
        if is_remote_application_href(spec.href):
            continue
        out.append(spec)
    return tuple(out)


def compile_application_asset_plan(
    specs: Sequence[ApplicationAssetSpec],
) -> ApplicationAssetPlan:
    """Compile a deterministic acyclic application asset plan.

    Returns ``ok=False`` with diagnostics for duplicate ids, missing deps,
    cycles, invalid kind/placement, remote CDN hrefs, fragment/inline scripts,
    and invalid CSP integrity values. Never fetches remote assets.
    """
    diagnostics: list[Diagnostic] = []
    by_id: dict[str, ApplicationAssetSpec] = {}

    for spec in specs:
        if spec.logical_id in by_id:
            diagnostics.append(
                make_diagnostic(
                    HED_ASSET_0531,
                    severity=DiagnosticSeverity.ERROR,
                    title="Duplicate application asset id",
                    explanation=f"logical_id {spec.logical_id!r} appears more than once.",
                    remediation="Use unique logical_id values in the asset plan.",
                    context={"logical_id": spec.logical_id},
                )
            )
            continue
        by_id[spec.logical_id] = spec
        _validate_spec(spec, diagnostics)

    for logical_id, spec in by_id.items():
        for dep in spec.depends_on:
            if dep not in by_id:
                diagnostics.append(
                    make_diagnostic(
                        HED_ASSET_0532,
                        severity=DiagnosticSeverity.ERROR,
                        title="Missing application asset dependency",
                        explanation=(
                            f"Asset {logical_id!r} depends on {dep!r}, which is not in the plan."
                        ),
                        remediation="Add the missing dependency or remove the depends_on edge.",
                        context={"logical_id": logical_id, "missing": dep},
                    )
                )

    cycle_nodes = _detect_cycles(by_id) if by_id else set()
    for node in sorted(cycle_nodes):
        diagnostics.append(
            make_diagnostic(
                HED_ASSET_0533,
                severity=DiagnosticSeverity.ERROR,
                title="Application asset dependency cycle",
                explanation=f"Cycle detected involving asset {node!r}.",
                remediation="Remove cyclic depends_on edges.",
                context={"logical_id": node},
            )
        )

    ok = not any(d.severity is DiagnosticSeverity.ERROR for d in diagnostics)
    ordered: tuple[ApplicationAssetSpec, ...] = ()
    if ok and by_id:
        ordered = tuple(_topo_order(by_id))
    elif by_id and not cycle_nodes and _deps_resolvable(by_id):
        # Stable inspection order when non-graph errors remain.
        ordered = tuple(_topo_order(by_id))

    return ApplicationAssetPlan(assets=ordered, diagnostics=tuple(diagnostics), ok=ok)


def _validate_spec(spec: ApplicationAssetSpec, diagnostics: list[Diagnostic]) -> None:
    if spec.kind not in VALID_APPLICATION_ASSET_KINDS:
        diagnostics.append(
            make_diagnostic(
                HED_ASSET_0535,
                severity=DiagnosticSeverity.ERROR,
                title="Invalid application asset kind",
                explanation=(
                    f"Asset {spec.logical_id!r} has kind {spec.kind!r}; "
                    f"expected one of {sorted(VALID_APPLICATION_ASSET_KINDS)}."
                ),
                remediation="Use kind 'css', 'js', or 'module'.",
                context={"logical_id": spec.logical_id, "kind": spec.kind},
            )
        )
    if spec.placement not in VALID_APPLICATION_ASSET_PLACEMENTS:
        diagnostics.append(
            make_diagnostic(
                HED_ASSET_0534,
                severity=DiagnosticSeverity.ERROR,
                title="Invalid application asset placement",
                explanation=(
                    f"Asset {spec.logical_id!r} has placement {spec.placement!r}; "
                    f"expected one of {sorted(VALID_APPLICATION_ASSET_PLACEMENTS)}."
                ),
                remediation="Use placement 'head', 'after_htmx_core', or 'body_end'.",
                context={"logical_id": spec.logical_id, "placement": spec.placement},
            )
        )
    if _is_remote_href(spec.href):
        diagnostics.append(
            make_diagnostic(
                HED_ASSET_0536,
                severity=DiagnosticSeverity.ERROR,
                title="Remote application asset rejected",
                explanation=(
                    f"Asset {spec.logical_id!r} href {spec.href!r} looks like a remote "
                    "CDN URL. Hedron application assets must be local."
                ),
                remediation="Vendor the asset locally and reference a same-origin path.",
                context={"logical_id": spec.logical_id, "href": spec.href},
            )
        )
    if spec.kind in {"js", "module"} and _is_fragment_or_inline_script(spec.href):
        diagnostics.append(
            make_diagnostic(
                HED_ASSET_0537,
                severity=DiagnosticSeverity.ERROR,
                title="Fragment or inline script rejected",
                explanation=(
                    f"Asset {spec.logical_id!r} href {spec.href!r} is not a local "
                    "script path (inline/data/javascript schemes are forbidden)."
                ),
                remediation=(
                    "Declare PAGE-shell scripts with local paths; fragments must not "
                    "install executable assets."
                ),
                context={"logical_id": spec.logical_id, "href": spec.href},
            )
        )
    if spec.integrity is not None and not _valid_integrity(spec.integrity):
        diagnostics.append(
            make_diagnostic(
                HED_ASSET_0538,
                severity=DiagnosticSeverity.ERROR,
                title="Invalid CSP integrity value",
                explanation=(
                    f"Asset {spec.logical_id!r} integrity {spec.integrity!r} is not a "
                    "valid sha256/sha384/sha512 Subresource Integrity digest."
                ),
                remediation="Provide integrity as 'sha256-<base64>' (or sha384/sha512).",
                context={"logical_id": spec.logical_id, "integrity": spec.integrity},
            )
        )


def is_remote_application_href(href: str) -> bool:
    """True for protocol-relative or any alphabetic ``scheme:`` href.

    Local assets are empty, root-relative (``/…``), or relative paths without a
    scheme. ``file://``, ``data:``, ``http(s):``, and similar schemes fail closed.
    """
    text = href.strip()
    if not text:
        return False
    if text.startswith("//"):
        return True
    # Root-relative same-origin paths are never remote.
    if text.startswith("/"):
        return False
    scheme, sep, _rest = text.partition(":")
    # Alphabetic scheme before the first path segment (file:, https:, data:, …).
    return bool(sep and scheme.isalpha())


def _is_remote_href(href: str) -> bool:
    return is_remote_application_href(href)


def _is_fragment_or_inline_script(href: str) -> bool:
    lowered = href.strip().lower()
    if not lowered:
        return True
    return (
        lowered.startswith("javascript:")
        or lowered.startswith("data:")
        or lowered.startswith("blob:")
        or "<script" in lowered
    )


def _valid_integrity(value: str) -> bool:
    text = value.strip()
    if not any(text.startswith(prefix) for prefix in _INTEGRITY_PREFIXES):
        return False
    digest = text.split("-", 1)[1]
    if not digest:
        return False
    # SRI digests are base64; reject whitespace and obvious garbage.
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")
    return all(ch in allowed for ch in digest)


def _deps_resolvable(by_id: dict[str, ApplicationAssetSpec]) -> bool:
    return all(dep in by_id for spec in by_id.values() for dep in spec.depends_on)


def _detect_cycles(by_id: dict[str, ApplicationAssetSpec]) -> set[str]:
    seen: set[str] = set()
    stack: set[str] = set()
    cyclic: set[str] = set()

    def visit(name: str) -> None:
        if name in seen:
            return
        if name in stack:
            cyclic.add(name)
            return
        stack.add(name)
        for dep in by_id[name].depends_on:
            if dep in by_id:
                visit(dep)
                if dep in cyclic:
                    cyclic.add(name)
        stack.remove(name)
        seen.add(name)

    for name in sorted(by_id):
        visit(name)
    return cyclic


def _topo_order(by_id: dict[str, ApplicationAssetSpec]) -> list[ApplicationAssetSpec]:
    """Deterministic Kahn topo-sort (sorted ready queue)."""
    remaining: dict[str, set[str]] = {
        name: {dep for dep in spec.depends_on if dep in by_id} for name, spec in by_id.items()
    }
    ready = sorted(name for name, deps in remaining.items() if not deps)
    ordered: list[str] = []
    while ready:
        name = ready.pop(0)
        ordered.append(name)
        for other, deps in remaining.items():
            if name in deps:
                deps.remove(name)
                if not deps and other not in ordered and other not in ready:
                    ready.append(other)
                    ready.sort()
    return [by_id[name] for name in ordered]


def specs_from_asset_refs(
    assets: Sequence[AssetRef],
    *,
    asset_attributes: Mapping[str, Mapping[str, str]] | None = None,
    registry_by_path: Mapping[str, ApplicationAssetSpec] | None = None,
) -> tuple[ApplicationAssetSpec, ...]:
    """Build specs from call-site :class:`AssetRef` values, enriching from registry."""
    out: list[ApplicationAssetSpec] = []
    seen_href: set[str] = set()
    for index, asset in enumerate(assets):
        href = asset.href.strip()
        if not href or href in seen_href:
            continue
        seen_href.add(href)
        reg = (registry_by_path or {}).get(href)
        attrs = dict(asset.attributes)
        if asset_attributes and href in asset_attributes:
            attrs.update(asset_attributes[href])
        integrity = attrs.get("integrity")
        if integrity is None and reg is not None:
            integrity = reg.integrity
        logical_id = reg.logical_id if reg is not None else f"callsite:{index}:{href}"
        out.append(
            ApplicationAssetSpec(
                logical_id=logical_id,
                kind=asset.kind,
                href=href,
                depends_on=reg.depends_on if reg is not None else (),
                placement=reg.placement if reg is not None else "head",
                integrity=integrity,
            )
        )
    return tuple(out)
