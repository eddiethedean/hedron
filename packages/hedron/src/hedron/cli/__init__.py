"""Hedron CLI: routes, components, preview, build, dev, inspect, eject."""

from __future__ import annotations

from hedron.cli.commands.check import (
    _check_htmx_region_mismatches as _check_htmx_region_mismatches,
)
from hedron.cli.commands.check import (
    _check_select_oob_conflicts as _check_select_oob_conflicts,
)
from hedron.cli.commands.check import (
    _compat_info_diagnostics as _compat_info_diagnostics,
)
from hedron.cli.commands.check import (
    _compat_surface_active as _compat_surface_active,
)
from hedron.cli.commands.check import (
    _registry_has_chart_surface as _registry_has_chart_surface,
)
from hedron.cli.commands.run import _cmd_run_app as _cmd_run_app
from hedron.cli.discovery import (
    _release_pin_bounds as _release_pin_bounds,
)
from hedron.cli.discovery import (
    _scaffold_dep as _scaffold_dep,
)
from hedron.cli.parser import main as main

__all__ = ["main"]
