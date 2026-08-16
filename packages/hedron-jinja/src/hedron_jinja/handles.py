"""Optional HDJ bridge from templates to registered 0.43 handles."""

from __future__ import annotations

from hedron_core.codes import HED_UPDATE_0003
from hedron_core.diagnostics import error
from hedron_core.updates import BaseHandleDescriptor, list_handle_descriptors

__all__ = ["resolve_registered_handle"]


def resolve_registered_handle(
    logical_id: str,
    *,
    app_id: str | None = None,
) -> BaseHandleDescriptor:
    """Return a registered handle descriptor. String-only implicit routes are refused."""
    token = str(logical_id).strip()
    if not token or "/" in token or token.startswith("http"):
        raise error(
            HED_UPDATE_0003,
            title="HDJ handle references must be registered logical ids",
            explanation=f"{logical_id!r} is not a registered handle id.",
            remediation="Pass a handle.logical_id from @app.refreshable / @app.command.",
        )
    matches = [
        item
        for item in list_handle_descriptors(app_id=app_id)
        if item.logical_id == token or item.name == token
    ]
    if len(matches) != 1:
        raise error(
            HED_UPDATE_0003,
            title="HDJ handle is not registered",
            explanation=f"No unique registered handle for {token!r}.",
            remediation="Register the view/command before referencing it from HDJ.",
        )
    return matches[0]
