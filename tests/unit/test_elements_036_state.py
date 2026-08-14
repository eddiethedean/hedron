"""STATE-036: ElementStateOwnership rules."""

from __future__ import annotations

import pytest

from hedron_core.diagnostics import HedronError
from hedron_core.registry import ElementFieldOwnership
from hedron_elements.state import apply_incoming_update, refuse_transfer, validate_field_ownership


def test_validate_modes() -> None:
    ok = validate_field_ownership(ElementFieldOwnership(name="status", mode="controlled"))
    assert ok.mode == "controlled"


def test_capability_cannot_be_local() -> None:
    with pytest.raises(HedronError) as exc:
        validate_field_ownership(ElementFieldOwnership(name="csrf_token", mode="local"))
    assert exc.value.diagnostic.code == "HED-ELEMENT-STATE-0002"


def test_dirty_draft_defaults_to_conflict() -> None:
    assert apply_incoming_update(mode="draft", dirty=True, policy=None) == "conflict"


def test_unproven_rebase_rejected() -> None:
    with pytest.raises(HedronError) as exc:
        apply_incoming_update(mode="draft", dirty=True, policy="rebase", allow_rebase=False)
    assert exc.value.diagnostic.code == "HED-ELEMENT-STATE-0004"


def test_transfer_refused() -> None:
    with pytest.raises(HedronError) as exc:
        refuse_transfer()
    assert exc.value.diagnostic.code == "HED-ELEMENT-STATE-0006"


def test_controlled_no_loop_policy() -> None:
    assert apply_incoming_update(mode="controlled", dirty=False, policy=None) == "replace"
