"""Thin Hedron(FastAPI) application facade."""

from __future__ import annotations

from hedron.app.hedron import Hedron
from hedron.static_mount import mount_build_assets, mount_hedron_static

__all__ = ["Hedron", "mount_build_assets", "mount_hedron_static"]
