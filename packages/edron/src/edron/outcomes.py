from __future__ import annotations

from typing import Any

from edron._internal import require_frame
from hedron import Outcome, OutcomeKind


def success(message: str | None = None, *, status_code: int = 200) -> Outcome:
    """Return the closed native success outcome."""
    if status_code != 200:
        raise ValueError("native Hedron 0.67 success outcomes use status_code=200")
    return Outcome.success(**({"message": message} if message is not None else {}))


def refresh(*targets: Any) -> Outcome:
    """Return a native refresh outcome for registered Edron views."""
    frame = require_frame("action")
    resolved: list[str] = []
    for target in targets:
        if hasattr(target, "fragment"):
            target = target.fragment
        native = frame.app._fragments.get(id(target))
        if native is None and hasattr(target, "_native"):
            native = target._native
        if native is None:
            native = target
        if hasattr(target, "arguments") and target.arguments:
            native = native.bind(**target.arguments)
        logical_id = getattr(native, "logical_id", None)
        if not isinstance(logical_id, str) or not logical_id.strip():
            raise TypeError("refresh targets must be registered Edron views")
        resolved.append(logical_id)
    if not resolved:
        raise ValueError("refresh requires at least one target")
    return Outcome(OutcomeKind.REFRESH, {"handles": resolved})
