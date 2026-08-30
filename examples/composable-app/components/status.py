"""Service-status components shared by pages and fragment routes."""

from __future__ import annotations

from hedron import Alert


def service_status(refreshed_at: str) -> Alert:
    """Build the replaceable status fragment."""
    return Alert(
        f"All services operational · refreshed {refreshed_at}",
        title="System status",
        tone="success",
    )
