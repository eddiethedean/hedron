"""Compatibility namespace backed by the shared :mod:`fastapi_workbench` core.

Hedron-Posit owns branding and Connect-specific composition, while path
normalization, discovery, diagnostics, and process supervision live in the
generic Workbench package.  The aliases preserve the historical private import
paths for downstream code during the 1.0 transition without maintaining a
second implementation.
"""

from __future__ import annotations

import importlib
import sys

_MODULES = (
    "codes",
    "config",
    "detect",
    "diagnostics",
    "middleware",
    "mount",
    "redact",
    "resolve",
    "runner",
    "urls",
)

for _name in _MODULES:
    _module = importlib.import_module(f"fastapi_workbench.{_name}")
    sys.modules.setdefault(f"{__name__}.{_name}", _module)
    globals()[_name] = _module

__all__ = ()
