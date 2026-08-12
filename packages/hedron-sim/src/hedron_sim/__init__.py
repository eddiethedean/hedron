"""Offline HTMX simulation for Hedron docs and static demos."""

from __future__ import annotations

from hedron_sim.app import SimApp, SimRoute
from hedron_sim.embed import embed_demo, render_handler_html, wrap_browser_chrome
from hedron_sim.subset import (
    DECLARED_HX_ATTRS,
    DECLARED_HX_METHODS,
    DECLARED_SWAP_STYLES,
    DEFAULT_SUBSET,
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
    "SIM_LOCAL_TIME",
    "SIM_UTC",
    "SimApp",
    "SimRoute",
    "UnsupportedSimFeatureError",
    "embed_demo",
    "render_handler_html",
    "require_supported_method",
    "require_supported_swap",
    "sim_form",
    "sim_local_time",
    "sim_utc",
    "subset_policy_markdown",
    "wrap_browser_chrome",
]

__version__ = "0.1.0"
