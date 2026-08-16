"""Negative fixture: a Hedron type-checker plugin is not required."""

from __future__ import annotations

# Intentionally no `hedron.plugins.mypy` / pyright plugin import.
from hedron import ViewParams

_ = ViewParams
