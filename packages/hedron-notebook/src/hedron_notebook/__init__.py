"""Server-side notebook preview helper for Hedron (experimental Alpha)."""

from __future__ import annotations

from hedron_notebook.features import inspect_features
from hedron_notebook.handles import (
    DISPLAY_SNAPSHOT_SCHEMA,
    REDACTED,
    DisplayHandle,
    NotebookSession,
    StaleDisplayHandleError,
    preview_handle,
    redact_text,
)
from hedron_notebook.preview import (
    PREVIEW_TOKEN_COOKIE,
    PREVIEW_TOKEN_HEADER,
    PREVIEW_TOKEN_QUERY,
    NotebookPreview,
    PreviewTokenGate,
    start_preview,
    wrap_preview_app,
)
from hedron_notebook.topology import (
    HED_NOTEBOOK_TOKEN,
    HED_NOTEBOOK_TOPOLOGY,
    LOOPBACK_HOSTS,
    NotebookTokenError,
    NotebookTopologyError,
    handoff_disposition,
    is_loopback_host,
    require_loopback_host,
    start_server_handoff,
)

__version__ = "0.2.4"

__all__ = [
    "DISPLAY_SNAPSHOT_SCHEMA",
    "HED_NOTEBOOK_TOKEN",
    "HED_NOTEBOOK_TOPOLOGY",
    "LOOPBACK_HOSTS",
    "PREVIEW_TOKEN_COOKIE",
    "PREVIEW_TOKEN_HEADER",
    "PREVIEW_TOKEN_QUERY",
    "REDACTED",
    "DisplayHandle",
    "NotebookPreview",
    "NotebookSession",
    "NotebookTokenError",
    "NotebookTopologyError",
    "PreviewTokenGate",
    "StaleDisplayHandleError",
    "__version__",
    "handoff_disposition",
    "inspect_features",
    "is_loopback_host",
    "preview_handle",
    "redact_text",
    "require_loopback_host",
    "start_preview",
    "start_server_handoff",
    "wrap_preview_app",
]
