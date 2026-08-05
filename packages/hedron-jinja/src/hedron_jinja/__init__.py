"""Public API for Hedron's Jinja integration."""

from __future__ import annotations

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

__version__ = "0.12.0"

__all__ = [
    "DynamicDependency",
    "DynamicDependencyManifest",
    "ForeignNamespace",
    "HedronJinja",
    "HedronJinjaExtension",
    "HdjContext",
    "ProductionInventory",
    "TemplateCapabilities",
    "TemplateDeclaration",
    "TemplateKind",
    "TemplateSource",
    "TemplateSpec",
    "TwoPhaseStream",
    "__version__",
    "build_production_inventory",
    "reconcile_csp",
]
