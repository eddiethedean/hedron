"""Public API for Hedron's Jinja integration."""

from __future__ import annotations

from hedron_jinja.async_io import (
    AsyncIoBudget,
    AsyncIoDeclaration,
    AsyncIoRegistry,
    async_io_session,
    run_declared_async_io,
)
from hedron_jinja.contracts import (
    HdjContext,
    TemplateCapabilities,
    TemplateDeclaration,
    TemplateKind,
    TemplateSource,
    TemplateSpec,
)
from hedron_jinja.integration import HedronJinja, HedronJinjaExtension, TwoPhaseStream
from hedron_jinja.inventory import (
    DynamicDependency,
    DynamicDependencyManifest,
    ForeignNamespace,
    ProductionInventory,
    build_production_inventory,
    reconcile_csp,
)
from hedron_jinja.providers import (
    ProviderManifest,
    charts_provider_manifest,
    data_provider_manifest,
    provider_available,
)

__version__ = "0.13.0"

__all__ = [
    "AsyncIoBudget",
    "AsyncIoDeclaration",
    "AsyncIoRegistry",
    "DynamicDependency",
    "DynamicDependencyManifest",
    "ForeignNamespace",
    "HedronJinja",
    "HedronJinjaExtension",
    "HdjContext",
    "ProductionInventory",
    "ProviderManifest",
    "TemplateCapabilities",
    "TemplateDeclaration",
    "TemplateKind",
    "TemplateSource",
    "TemplateSpec",
    "TwoPhaseStream",
    "__version__",
    "async_io_session",
    "build_production_inventory",
    "charts_provider_manifest",
    "data_provider_manifest",
    "provider_available",
    "reconcile_csp",
    "run_declared_async_io",
]
