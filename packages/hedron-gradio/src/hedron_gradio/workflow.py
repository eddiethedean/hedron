"""Explicit Gradio RemoteWorkflow wrapping the shipped client adapter."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from hedron_core.bundles import FeatureBundle, FeatureConflictError, FeatureRequirement
from hedron_core.catalog import PackageProjection, ProjectionCapability
from hedron_core.codes import HED_BUNDLE_0007
from hedron_core.diagnostics import DiagnosticSeverity, make_diagnostic
from hedron_gradio.client import GradioClientAdapter, GradioEndpoint
from hedron_gradio.policy import GradioRemoteConfig

__all__ = ["RemoteWorkflow"]


@dataclass(frozen=True, slots=True)
class RemoteWorkflow:
    """Allowlisted Gradio endpoint → Hedron feature. Catalog presence is not exposure."""

    adapter: GradioClientAdapter
    endpoint: GradioEndpoint
    input_model: type[Any]
    outcomes: Mapping[str, Any]
    provider: str = "hedron-gradio"
    provider_version: str = "0.2.0"
    name: str | None = None

    def __post_init__(self) -> None:
        if not self.adapter.enabled:
            raise FeatureConflictError(
                make_diagnostic(
                    HED_BUNDLE_0007,
                    severity=DiagnosticSeverity.ERROR,
                    title="RemoteWorkflow requires an enabled Gradio adapter",
                    explanation="consume_catalog never enables Gradio or discovers endpoints.",
                    remediation=(
                        "Pass GradioClientAdapter(..., enabled=True) with an allowlisted host."
                    ),
                )
            )
        config = self.adapter.remote_config
        if not isinstance(config, GradioRemoteConfig):
            raise FeatureConflictError(
                make_diagnostic(
                    HED_BUNDLE_0007,
                    severity=DiagnosticSeverity.ERROR,
                    title="RemoteWorkflow requires GradioRemoteConfig",
                    explanation="Remote metadata cannot override local models or authz.",
                    remediation="Attach GradioRemoteConfig.from_base_url(...) before including.",
                )
            )
        names = {item.name for item in self.adapter.endpoints}
        empty = not names
        if empty or self.endpoint.name not in names:
            if empty:
                explanation = (
                    "An enabled Gradio adapter with an empty endpoints allowlist exposes nothing."
                )
            else:
                explanation = f"Endpoint {self.endpoint.name!r} is outside the adapter allowlist."
            raise FeatureConflictError(
                make_diagnostic(
                    HED_BUNDLE_0007,
                    severity=DiagnosticSeverity.ERROR,
                    title="Gradio endpoint is not allowlisted",
                    explanation=explanation,
                    remediation="Declare the endpoint on GradioClientAdapter.endpoints.",
                )
            )

    def to_bundle(self) -> FeatureBundle:
        ident = self.name or f"{self.provider}:{self.endpoint.name}"
        return FeatureBundle(
            logical_id=ident,
            provider=self.provider,
            provider_version=self.provider_version,
            projections=(
                PackageProjection(
                    namespace=f"hedron.gradio.workflow.{ident.replace(':', '.')}",
                    provider=self.provider,
                    provider_version=self.provider_version,
                    capabilities=(
                        ProjectionCapability(name="RemoteWorkflow", support="supported"),
                    ),
                    data={
                        "endpoint": self.endpoint.name,
                        "api_name": self.endpoint.api_name,
                        "input_model": getattr(self.input_model, "__name__", "model"),
                        "consume_catalog_exposes": False,
                    },
                    limitations=(
                        "allowlisted adapter/endpoint only",
                        "remote metadata is untrusted",
                    ),
                ),
            ),
            requirements=(FeatureRequirement(name="hedron-gradio", required=True),),
        )
