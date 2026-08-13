"""Gradio remote interop errors."""

from __future__ import annotations

__all__ = ["GradioRemoteError"]


class GradioRemoteError(Exception):
    """Raised when a remote Gradio call or policy check fails."""
