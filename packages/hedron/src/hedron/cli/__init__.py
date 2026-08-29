"""Hedron CLI: routes, components, preview, build, dev, inspect, eject."""

from __future__ import annotations

from hedron.cli.commands.check import (
    check_htmx_region_mismatches,
    check_select_oob_conflicts,
    compat_info_diagnostics,
    compat_surface_active,
    registry_has_chart_surface,
)
from hedron.cli.commands.run import cmd_run_app
from hedron.cli.discovery import release_pin_bounds, scaffold_dep
from hedron.cli.parser import main as main

_check_htmx_region_mismatches = check_htmx_region_mismatches
_check_select_oob_conflicts = check_select_oob_conflicts
_compat_info_diagnostics = compat_info_diagnostics
_compat_surface_active = compat_surface_active
_registry_has_chart_surface = registry_has_chart_surface
_cmd_run_app = cmd_run_app
_release_pin_bounds = release_pin_bounds
_scaffold_dep = scaffold_dep

__all__ = ["main"]
