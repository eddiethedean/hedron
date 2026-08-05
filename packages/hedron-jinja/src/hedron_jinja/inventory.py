"""Finite fingerprinted dynamic-dependency manifests and foreign namespaces (0.11)."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypedDict, cast

from hedron_core.diagnostics import error
from hedron_core.typing_aliases import JsonObject, JsonValue

__all__ = [
    "DynamicDependency",
    "DynamicDependencyManifest",
    "ForeignNamespace",
    "build_production_inventory",
    "reconcile_csp",
]


class TemplateInventoryReport(TypedDict, total=False):
    """JSON-shaped production inventory row for one HDJ template."""

    name: str
    kind: str
    capabilities: list[str]
    error: str


@dataclass(frozen=True, slots=True)
class DynamicDependency:
    """One fingerprinted dynamic dependency candidate (never a bare namespace)."""

    logical_id: str
    path: str
    digest: str
    size: int

    @classmethod
    def from_bytes(cls, logical_id: str, path: str, payload: bytes) -> DynamicDependency:
        digest = hashlib.sha256(payload).hexdigest()
        return cls(logical_id=logical_id, path=path, digest=digest, size=len(payload))


@dataclass(frozen=True, slots=True)
class ForeignNamespace:
    """Explicit foreign Jinja / package namespace boundary."""

    name: str
    root: str
    package: str | None = None
    shadow_allowed: bool = False


@dataclass(frozen=True, slots=True)
class DynamicDependencyManifest:
    """Finite set of fingerprinted dynamic dependency candidates."""

    version: int = 1
    dependencies: tuple[DynamicDependency, ...] = ()
    foreign_namespaces: tuple[ForeignNamespace, ...] = ()

    def __post_init__(self) -> None:
        ids = [d.logical_id for d in self.dependencies]
        if len(ids) != len(set(ids)):
            raise ValueError("dynamic dependency logical_ids must be unique")
        names = [n.name for n in self.foreign_namespaces]
        if len(names) != len(set(names)):
            raise ValueError("foreign namespace names must be unique")

    def fingerprint(self) -> str:
        payload = json.dumps(
            {
                "version": self.version,
                "dependencies": [
                    {
                        "logical_id": d.logical_id,
                        "path": d.path,
                        "digest": d.digest,
                        "size": d.size,
                    }
                    for d in self.dependencies
                ],
                "foreign_namespaces": [
                    {
                        "name": n.name,
                        "root": n.root,
                        "package": n.package,
                        "shadow_allowed": n.shadow_allowed,
                    }
                    for n in self.foreign_namespaces
                ],
            },
            sort_keys=True,
        ).encode()
        return hashlib.sha256(payload).hexdigest()

    def require_bound(self, logical_id: str) -> DynamicDependency:
        for dep in self.dependencies:
            if dep.logical_id == logical_id:
                return dep
        raise error(
            "HED-HDJ-0111",
            title="Dynamic dependency not bound",
            explanation=(
                f"Loader namespace alone is never a dependency bound; "
                f"{logical_id!r} is missing from the fingerprinted manifest."
            ),
            remediation="Add an exact fingerprinted candidate to the dynamic dependency manifest.",
        )

    def prevent_shadow(self, name: str, *, package_root: str) -> None:
        for ns in self.foreign_namespaces:
            if ns.name == name and not ns.shadow_allowed and Path(ns.root) != Path(package_root):
                raise error(
                    "HED-HDJ-0112",
                    title="Foreign namespace shadow rejected",
                    explanation=f"Namespace {name!r} would shadow {ns.root!r}.",
                    remediation=(
                        "Use a distinct namespace or set shadow_allowed with an explicit audit."
                    ),
                )


def reconcile_csp(
    policy_csp: str | None,
    *,
    required_capabilities: Sequence[str],
    source_name: str = "<hdj>",
    line: int = 1,
) -> list[str]:
    """Fail closed when HDJ capabilities would silently weaken SecurityPolicy CSP.

    Returns a list of mismatch messages (empty when reconciled). Callers must treat
    non-empty results as hard failures — never inject unsafe-inline/eval/nonces.
    """
    mismatches: list[str] = []
    csp = (policy_csp or "").lower()
    has_script_src = "script-src" in csp
    for capability in required_capabilities:
        if capability == "browser.inline-script":
            authorized = has_script_src and (
                "'unsafe-inline'" in csp or "nonce-" in csp or "'strict-dynamic'" in csp
            )
            if not authorized:
                mismatches.append(
                    f"{source_name}:{line}: capability {capability!r} conflicts with CSP "
                    f"(missing explicit inline/nonce/strict-dynamic authorization)"
                )
        if capability == "htmx.eval" and (not has_script_src or "unsafe-eval" not in csp):
            mismatches.append(
                f"{source_name}:{line}: capability {capability!r} requires explicit "
                f"unsafe-eval authorization in SecurityPolicy CSP"
            )
        if capability.startswith("network.") and "https://" in capability:
            origin = capability.split(":", 1)[-1]
            if origin and origin not in csp:
                mismatches.append(
                    f"{source_name}:{line}: remote origin {origin!r} is not present in CSP"
                )
    return mismatches


@dataclass
class ProductionInventory:
    templates: list[JsonObject] = field(default_factory=list)
    dynamic_manifest_fingerprint: str | None = None
    capabilities: list[str] = field(default_factory=list)
    foreign_namespaces: list[str] = field(default_factory=list)

    def as_dict(self) -> JsonObject:
        return {
            "templates": list(self.templates),
            "dynamic_manifest_fingerprint": self.dynamic_manifest_fingerprint,
            "capabilities": list(self.capabilities),
            "foreign_namespaces": list(self.foreign_namespaces),
        }


def build_production_inventory(
    *,
    template_reports: Sequence[Mapping[str, JsonValue] | TemplateInventoryReport] = (),
    manifest: DynamicDependencyManifest | None = None,
    capabilities: Sequence[str] = (),
) -> ProductionInventory:
    inv = ProductionInventory(
        templates=[cast(JsonObject, dict(t)) for t in template_reports],
        capabilities=list(capabilities),
    )
    if manifest is not None:
        inv.dynamic_manifest_fingerprint = manifest.fingerprint()
        inv.foreign_namespaces = [n.name for n in manifest.foreign_namespaces]
    return inv
