"""Public API for Hedron's Jinja integration."""

from __future__ import annotations

from hedron_jinja.async_io import (
    AsyncIoBudget,
    AsyncIoDeclaration,
    AsyncIoRegistry,
    async_io_session,
    run_declared_async_io,
)
from hedron_jinja.binding import ApplicationStyleFact, JinjaBinding
from hedron_jinja.contracts import (
    HdjContext,
    TemplateCapabilities,
    TemplateDeclaration,
    TemplateKind,
    TemplateSource,
    TemplateSpec,
)
from hedron_jinja.handles import (
    catalog_command_form,
    catalog_view,
    coerce_interaction_target,
    list_feature_bundles,
    resolve_registered_handle,
)
from hedron_jinja.instrumentation import (
    ExtensionEvidence,
    ExtensionRegistry,
    LoopMacroBudget,
    LoopMacroCounters,
    a11y_static_diagnostics,
    checker_fixture_from_diagnostics,
    instrumentation_session,
    portable_checker_json,
    record_loop_iteration,
    record_macro_call,
    register_htmx_catalog,
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
    elements_provider_manifest,
    extras_provider_manifest,
    maps_provider_manifest,
    provider_available,
)
from hedron_jinja.source import validate_element_declarations
from hedron_jinja.type_authoring import refuse_annotation_evaluation, registered_type_schema

__version__ = "1.0.7"

__all__ = [
    "AsyncIoBudget",
    "AsyncIoDeclaration",
    "AsyncIoRegistry",
    "ApplicationStyleFact",
    "DynamicDependency",
    "DynamicDependencyManifest",
    "ExtensionEvidence",
    "ExtensionRegistry",
    "ForeignNamespace",
    "HedronJinja",
    "HedronJinjaExtension",
    "HdjContext",
    "JinjaBinding",
    "LoopMacroBudget",
    "LoopMacroCounters",
    "ProductionInventory",
    "ProviderManifest",
    "TemplateCapabilities",
    "TemplateDeclaration",
    "TemplateKind",
    "TemplateSource",
    "TemplateSpec",
    "TwoPhaseStream",
    "__version__",
    "a11y_static_diagnostics",
    "async_io_session",
    "build_production_inventory",
    "catalog_command_form",
    "catalog_view",
    "charts_provider_manifest",
    "checker_fixture_from_diagnostics",
    "coerce_interaction_target",
    "data_provider_manifest",
    "elements_provider_manifest",
    "extras_provider_manifest",
    "instrumentation_session",
    "list_feature_bundles",
    "maps_provider_manifest",
    "portable_checker_json",
    "provider_available",
    "refuse_annotation_evaluation",
    "reconcile_csp",
    "record_loop_iteration",
    "resolve_registered_handle",
    "record_macro_call",
    "register_htmx_catalog",
    "registered_type_schema",
    "run_declared_async_io",
    "validate_element_declarations",
]
