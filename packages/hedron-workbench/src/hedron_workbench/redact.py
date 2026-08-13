"""Compatibility re-export from hedron_posit.redact."""

from __future__ import annotations

from hedron_posit.redact import (
    redact_path,
    redact_query,
    redact_record,
    redact_scope_for_log,
    redact_text,
    redact_url,
)

__all__ = [
    "redact_path",
    "redact_query",
    "redact_record",
    "redact_scope_for_log",
    "redact_text",
    "redact_url",
]
