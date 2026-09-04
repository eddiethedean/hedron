"""Offline HTMX simulation for Hedron docs and static demos."""

from __future__ import annotations

from hedron_sim.app import SimApp, SimRoute
from hedron_sim.embed import embed_demo, render_handler_html, wrap_browser_chrome
from hedron_sim.features import inspect_features
from hedron_sim.manifest import (
    MANIFEST_CATEGORIES,
    SIM_MANIFEST_SCHEMA,
    ManifestEntry,
    divergence_manifest,
    manifest_entry,
    manifest_markdown,
    require_supported_feature,
    subset_manifest,
)
from hedron_sim.parity import (
    PARITY_FIXTURES,
    PARITY_SCHEMA,
    compare_parity,
    normalize_parity_html,
)
from hedron_sim.recording import (
    HED_SIM_LIMIT,
    SIM_SCENARIO_SCHEMA,
    SimClock,
    SimEvent,
    SimLimitError,
    SimLimits,
    SimRecorder,
    SimScenario,
    export_scenario,
    import_scenario,
)
from hedron_sim.subset import (
    DECLARED_HX_ATTRS,
    DECLARED_HX_METHODS,
    DECLARED_SWAP_STYLES,
    DEFAULT_SUBSET,
    HED_SIM_UNSUPPORTED,
    UnsupportedSimFeatureError,
    require_supported_method,
    require_supported_swap,
    subset_policy_markdown,
)
from hedron_sim.tokens import SIM_LOCAL_TIME, SIM_UTC, sim_form, sim_local_time, sim_utc

__all__ = [
    "DECLARED_HX_ATTRS",
    "DECLARED_HX_METHODS",
    "DECLARED_SWAP_STYLES",
    "DEFAULT_SUBSET",
    "HED_SIM_LIMIT",
    "HED_SIM_UNSUPPORTED",
    "MANIFEST_CATEGORIES",
    "PARITY_FIXTURES",
    "PARITY_SCHEMA",
    "SIM_LOCAL_TIME",
    "SIM_MANIFEST_SCHEMA",
    "SIM_SCENARIO_SCHEMA",
    "SIM_UTC",
    "ManifestEntry",
    "SimApp",
    "SimClock",
    "SimEvent",
    "SimLimitError",
    "SimLimits",
    "SimRecorder",
    "SimRoute",
    "SimScenario",
    "UnsupportedSimFeatureError",
    "compare_parity",
    "divergence_manifest",
    "embed_demo",
    "export_scenario",
    "import_scenario",
    "inspect_features",
    "manifest_entry",
    "manifest_markdown",
    "normalize_parity_html",
    "render_handler_html",
    "require_supported_feature",
    "require_supported_method",
    "require_supported_swap",
    "sim_form",
    "sim_local_time",
    "sim_utc",
    "subset_manifest",
    "subset_policy_markdown",
    "wrap_browser_chrome",
]

__version__ = "0.2.3"
