"""CAP-055 evidence."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from hedron.capabilities import (
    MappingCapabilityProvider,
    enforce_capability,
    evaluate_capability,
)
from hedron_core.diagnostics import HedronError


def test_issue_546_denied_capability_cannot_bypass_action() -> None:
    request = SimpleNamespace(
        app=SimpleNamespace(
            state=SimpleNamespace(hedron_capabilities=MappingCapabilityProvider(set()))
        )
    )
    decision = evaluate_capability(request, "items.edit")
    assert decision.allowed is False
    assert decision.presentation in {"hide", "disable"}
    with pytest.raises(HedronError) as exc:
        enforce_capability(request, "items.edit")
    assert "HED-CAP-0001" in str(exc.value)


def test_capability_metadata_redacted() -> None:
    request = SimpleNamespace(
        app=SimpleNamespace(
            state=SimpleNamespace(hedron_capabilities=MappingCapabilityProvider({"items.edit"}))
        )
    )
    decision = evaluate_capability(request, "items.edit")
    redacted = decision.redacted()
    assert redacted["allowed"] is True
    assert "policy" not in redacted
