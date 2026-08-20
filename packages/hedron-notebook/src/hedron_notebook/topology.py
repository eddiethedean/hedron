"""Notebook network topology, token failures, and opt-in real-server handoff.

The notebook preview is a localhost development aid, not a server product. This
module owns the two deterministic boundaries: a non-loopback bind is rejected,
and a handoff to a real development server must print its exact security and
topology disposition before anything is started.
"""

from __future__ import annotations

import ipaddress
from collections.abc import Callable
from typing import Any

__all__ = [
    "HED_NOTEBOOK_TOKEN",
    "HED_NOTEBOOK_TOPOLOGY",
    "LOOPBACK_HOSTS",
    "NotebookTokenError",
    "NotebookTopologyError",
    "handoff_disposition",
    "is_loopback_host",
    "require_loopback_host",
    "start_server_handoff",
]

# Mirrors hedron_conformance.authoring_loop.HED_NOTEBOOK_*. hedron-notebook does not
# depend on hedron-conformance; tests/unit/test_notebook_054.py asserts they agree.
HED_NOTEBOOK_TOPOLOGY = "HED-NOTEBOOK-TOPOLOGY"
HED_NOTEBOOK_TOKEN = "HED-NOTEBOOK-TOKEN"

LOOPBACK_HOSTS = frozenset({"localhost", "127.0.0.1", "::1", "0:0:0:0:0:0:0:1"})


class NotebookTopologyError(ValueError):
    """Raised when a preview or handoff would leave the loopback interface."""

    code: str = HED_NOTEBOOK_TOPOLOGY

    def __init__(self, message: str, *, host: str = "") -> None:
        super().__init__(message)
        self.host = host


class NotebookTokenError(ValueError):
    """Raised when a preview session token is missing, empty, or rejected."""

    code: str = HED_NOTEBOOK_TOKEN

    def __init__(self, message: str, *, source: str = "") -> None:
        super().__init__(message)
        self.source = source


def is_loopback_host(host: str) -> bool:
    """Return ``True`` when ``host`` names the loopback interface."""
    normalized = host.strip().lower().strip("[]")
    if normalized in LOOPBACK_HOSTS:
        return True
    try:
        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        return False


def require_loopback_host(host: str, *, surface: str = "preview") -> str:
    """Return ``host`` when it is loopback, else fail with the topology code."""
    if not is_loopback_host(host):
        raise NotebookTopologyError(
            f"hedron-notebook {surface} refuses non-loopback host {host!r}. "
            "Supported preview binds only to loopback (localhost / 127.0.0.1 / ::1). "
            "Remote or public serving is not part of the Supported API.",
            host=host,
        )
    return host


def handoff_disposition(
    *,
    host: str = "127.0.0.1",
    port: int = 0,
    root_path: str = "",
    token_gated: bool = True,
    allow_public: bool = False,
    app_label: str = "asgi-app",
) -> str:
    """Return the exact security/topology disposition of a real-server handoff.

    The string is written for a human reading a notebook cell: it states the bind
    interface, whether the token gate stays on, and that public promotion is
    refused. It never contains a token value.
    """
    bind = f"{host}:{port}" if port else f"{host}:<ephemeral>"
    lines = [
        "hedron-notebook real-server handoff disposition",
        f"- application: {app_label}",
        f"- bind: {bind}{root_path or ''}",
        f"- interface: {'loopback' if is_loopback_host(host) else 'NON-LOOPBACK (refused)'}",
        f"- token gate: {'required' if token_gated else 'DISABLED (refused)'}",
        f"- public hosting: {'requested (refused)' if allow_public else 'refused by default'}",
        "- promotion: never automatic; the embedded preview stays localhost-only",
        f"- failure code on violation: {HED_NOTEBOOK_TOPOLOGY}",
    ]
    return "\n".join(lines)


def start_server_handoff(
    app: Any,
    *,
    host: str = "127.0.0.1",
    port: int = 0,
    root_path: str = "",
    token_gated: bool = True,
    allow_public: bool = False,
    printer: Callable[[str], None] | None = None,
) -> str:
    """Print the handoff disposition for ``app`` and return it without binding.

    This is the opt-in seam to a real development server: it hands the author the
    exact disposition to review, and refuses public or untokenized topologies. It
    deliberately starts nothing, so no socket is ever bound to ``0.0.0.0``.
    """
    if allow_public:
        raise NotebookTopologyError(
            "hedron-notebook refuses allow_public=True; public hosting is not part of "
            "the Supported API. Deploy with a real server outside the notebook instead.",
            host=host,
        )
    if not token_gated:
        raise NotebookTokenError(
            "hedron-notebook refuses an untokenized handoff; the preview token gate "
            "must stay enabled.",
            source="handoff",
        )
    require_loopback_host(host, surface="handoff")
    disposition = handoff_disposition(
        host=host,
        port=port,
        root_path=root_path,
        token_gated=token_gated,
        allow_public=allow_public,
        app_label=type(app).__name__,
    )
    emit = printer if printer is not None else print
    emit(disposition)
    return disposition
