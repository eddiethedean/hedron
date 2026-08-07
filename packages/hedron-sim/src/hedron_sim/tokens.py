"""Build-time and runtime placeholder tokens for dynamic sim responses."""

from __future__ import annotations

SIM_UTC = "__HEDRON_SIM_UTC__"
SIM_LOCAL_TIME = "__HEDRON_SIM_LOCAL_TIME__"

__all__ = ["SIM_LOCAL_TIME", "SIM_UTC", "sim_local_time", "sim_utc"]


def sim_utc() -> str:
    """Placeholder replaced by the JS runtime with the current UTC ``HH:MM:SS UTC`` stamp."""
    return SIM_UTC


def sim_local_time() -> str:
    """Placeholder replaced by the JS runtime with a short local clock string."""
    return SIM_LOCAL_TIME
