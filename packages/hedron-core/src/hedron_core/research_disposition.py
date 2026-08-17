"""RESEARCH-049: quarantined experimental dispositions. Not public exports."""

from __future__ import annotations

from hedron_core.codes import HED_FP_0008
from hedron_core.diagnostics import error

RESEARCH_CANDIDATES = ("partial-validation", "missing-sentinel", "fail-fast")
RESEARCH_SUPPORTED: tuple[str, ...] = ()
RESEARCH_DISPOSITIONS: dict[str, str] = {
    "partial-validation": "experimental",
    "missing-sentinel": "exclude",
    "fail-fast": "experimental",
}
# Pydantic MISSING and FailFast must never appear in hedron.__all__.
EXPERIMENTAL_SYMBOLS = ("FailFast", "MISSING")


def refuse_supported_research(name: str) -> None:
    """Fail closed if a quarantined research feature is claimed Supported."""
    if name in RESEARCH_CANDIDATES or name in EXPERIMENTAL_SYMBOLS:
        raise error(
            HED_FP_0008,
            title="Research feature is not Supported",
            explanation=f"{name!r} is quarantined by RESEARCH-049.",
            remediation="Keep FailFast/MISSING/partial-validation off public surfaces.",
        )
