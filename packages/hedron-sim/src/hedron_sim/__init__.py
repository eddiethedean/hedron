"""Offline HTMX simulation for Hedron docs and static demos."""

from __future__ import annotations

from hedron_sim.app import SimApp, SimRoute
from hedron_sim.embed import embed_demo, render_handler_html, wrap_browser_chrome
from hedron_sim.tokens import SIM_LOCAL_TIME, SIM_UTC, sim_form, sim_local_time, sim_utc

__all__ = [
    "SIM_LOCAL_TIME",
    "SIM_UTC",
    "SimApp",
    "SimRoute",
    "embed_demo",
    "render_handler_html",
    "sim_form",
    "sim_local_time",
    "sim_utc",
    "wrap_browser_chrome",
]

__version__ = "0.1.0"
