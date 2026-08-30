"""SETTINGS-049 dispositions. No pydantic-settings on the flagship train."""

from __future__ import annotations

from hedron_core.codes import HED_FP_0008
from hedron_core.diagnostics import error

SETTINGS_CANDIDATES = ("fastapi-workbench", "hedron-posit")
NOT_CANDIDATES = ("hedron", "hedron-core", "hedron.config.HedronSettings")
ALLOWED = ("adopt", "retain-custom-loader")

# Spike evidence: argparse WorkbenchConfig loaders keep source precedence,
# unknown-key rejection, and no import-time I/O. pydantic-settings is not adopted.
SETTINGS_DISPOSITIONS: dict[str, str] = {
    "fastapi-workbench": "retain-custom-loader",
    "hedron-posit": "retain-custom-loader",
}


def refuse_hedron_settings_evaluation() -> None:
    """D-084: hedron.config.HedronSettings is not a SETTINGS-049 candidate."""
    raise error(
        HED_FP_0008,
        title="HedronSettings is not a settings-spike candidate",
        explanation="Only fastapi-workbench and hedron-posit were evaluated.",
        remediation="Keep argparse/custom loaders unless a later spike records adopt.",
    )
