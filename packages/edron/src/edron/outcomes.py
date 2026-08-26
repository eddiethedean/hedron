from __future__ import annotations

from typing import Any

from edron._internal import require_frame
from hedron import InteractionResult, RefreshIntent
from hedron import refresh as _native_refresh

Outcome = InteractionResult | RefreshIntent | Any


def success(message: str | None = None, *, status_code: int = 200) -> InteractionResult:
    content = None
    if message is not None:
        from hedron import Status

        content = Status(message, tone="success")
    return InteractionResult(content=content, status_code=status_code, swap="none")


def refresh(*targets: Any) -> RefreshIntent:
    frame = require_frame("action")
    resolved = []
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
        resolved.append(native)
    return _native_refresh(*resolved)
