"""Explicit MCP exposure wrapping live McpProjection registration."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Literal

from hedron_core.bundles import FeatureBundle, FeatureConflictError, FeatureRequirement
from hedron_core.catalog import PackageProjection, ProjectionCapability
from hedron_core.codes import HED_BUNDLE_0002, HED_BUNDLE_0007
from hedron_core.diagnostics import DiagnosticSeverity, make_diagnostic
from hedron_mcp.server import McpProjection, McpResource, McpTool, package_version

__all__ = ["McpExposure"]


@dataclass(frozen=True, slots=True)
class McpExposure:
    """Deny-by-default catalog-entry exposure. Catalog presence grants nothing."""

    catalog_id: str
    role: Literal["resource", "tool"]
    projection: McpProjection
    name: str
    authorize: Callable[..., None]
    schema: Mapping[str, Any] | None = None
    mutate: bool = False
    uri: str = ""
    handler: Callable[..., Any] | None = None
    description: str = ""

    def apply(self) -> None:
        if not self.projection.enabled:
            raise FeatureConflictError(
                make_diagnostic(
                    HED_BUNDLE_0007,
                    severity=DiagnosticSeverity.ERROR,
                    title="McpExposure requires an enabled McpProjection",
                    explanation="Catalog presence and consume_catalog() never grant exposure.",
                    remediation="Construct McpProjection(enabled=True) and call live authorize.",
                )
            )
        if self.role == "resource":
            try:
                self.projection.register_resource(
                    McpResource(
                        uri=self.uri or f"hedron://{self.catalog_id}",
                        name=self.name,
                        description=self.description,
                        authorize=self.authorize,
                    )
                )
            except ValueError as exc:
                raise FeatureConflictError(
                    make_diagnostic(
                        HED_BUNDLE_0002,
                        severity=DiagnosticSeverity.ERROR,
                        title="MCP exposure already registered",
                        explanation=str(exc),
                        remediation=(
                            "Use a distinct tool or resource name, or eject the existing bundle."
                        ),
                    )
                ) from exc
            return
        handler = self.handler
        if handler is None:
            raise FeatureConflictError(
                make_diagnostic(
                    HED_BUNDLE_0007,
                    severity=DiagnosticSeverity.ERROR,
                    title="MCP tool exposure requires a handler",
                    explanation="Tools wrap an explicit ActionHandle or typed function.",
                    remediation="Pass handler= the live authorized function.",
                )
            )
        try:
            self.projection.register_tool(
                McpTool(
                    name=self.name,
                    schema=dict(self.schema or {}),
                    mutate=self.mutate,
                    handler=handler,
                    description=self.description,
                    authorize=self.authorize,
                )
            )
        except ValueError as exc:
            raise FeatureConflictError(
                make_diagnostic(
                    HED_BUNDLE_0002,
                    severity=DiagnosticSeverity.ERROR,
                    title="MCP exposure already registered",
                    explanation=str(exc),
                    remediation=(
                        "Use a distinct tool or resource name, or eject the existing bundle."
                    ),
                )
            ) from exc

    def unapply(self) -> None:
        if self.role == "resource":
            self.projection.unregister_resource(self.uri or f"hedron://{self.catalog_id}")
        else:
            self.projection.unregister_tool(self.name)

    def to_bundle(self) -> FeatureBundle:
        return FeatureBundle(
            logical_id=f"hedron-mcp:{self.name}",
            provider="hedron-mcp",
            provider_version=package_version(),
            projections=(
                PackageProjection(
                    namespace=f"hedron.mcp.exposure.{self.name}",
                    provider="hedron-mcp",
                    provider_version=package_version(),
                    capabilities=(ProjectionCapability(name="McpExposure", support="supported"),),
                    data={
                        "catalog_id": self.catalog_id,
                        "role": self.role,
                        "name": self.name,
                        "exposure": True,
                        "consume_catalog_exposes": False,
                    },
                    limitations=(
                        "explicit opt-in; live authorize; catalog presence is not exposure",
                    ),
                ),
            ),
            requirements=(FeatureRequirement(name="hedron-mcp", required=True),),
        )
