"""Phase 0.61 lifecycle and surface contract coverage."""

from __future__ import annotations

import pytest

from hedron_core import (
    ActionPhase,
    ActionPolicy,
    ActionState,
    ActionTrace,
    AmbientBackdrop,
    AsyncRegion,
    Container,
    InteractionResult,
    NavGroup,
    OperationIdentity,
    Tabs,
    complete_operation,
    render,
)
from hedron_core.action_state import ActionTransitionError, begin_operation, transition_action
from hedron_core.htmx.headers import interaction_trace
from hedron_elements.action_async import ActionAsync


def test_action_state_lifecycle_and_explicit_retry_policy() -> None:
    operation = OperationIdentity("save-1", target="#editor")
    state, accepted = begin_operation(ActionState(), operation)
    assert accepted and state.phase is ActionPhase.PENDING
    assert state.to_dict()["schema"] == "hedron.action-state.v1"
    assert state.operation is not None and state.operation.to_dict()["operation_id"] == "save-1"

    state, accepted = complete_operation(
        state,
        ActionPhase.ERROR,
        operation,
        message="Try again",
        retryable=True,
    )
    assert accepted and state.retryable

    retry_policy = ActionPolicy(
        allow_retry=True,
        max_attempts=2,
        idempotent=True,
    )
    retry, accepted = begin_operation(state, operation.next_generation(), policy=retry_policy)
    assert accepted and retry.phase is ActionPhase.PENDING
    assert retry.operation is not None and retry.operation.generation == 1


def test_stale_operation_result_cannot_replace_current_presentation() -> None:
    operation = OperationIdentity("refresh", generation=2, target="#panel")
    state, _ = begin_operation(ActionState(), operation)
    stale = OperationIdentity("refresh", generation=1, target="#panel")
    unchanged, accepted = complete_operation(state, ActionPhase.SUCCESS, stale)
    assert not accepted
    assert unchanged == state


def test_invalid_transition_is_rejected() -> None:
    with pytest.raises(ActionTransitionError):
        transition_action(ActionState(), ActionPhase.SUCCESS)


def test_trace_redacts_secret_like_facts_and_is_bounded() -> None:
    trace = ActionTrace(max_events=1).append(
        ActionPhase.ERROR,
        operation=OperationIdentity("op", target="#main"),
        facts={"token": "secret", "message": "x"},
    )
    assert len(trace.events) == 1
    assert trace.to_dict()["events"][0]["facts"]["token"] == "[redacted]"


def test_interaction_result_projects_action_state_and_trace() -> None:
    operation = OperationIdentity("op", generation=3, target="#main")
    state = ActionState(phase=ActionPhase.SUCCESS, operation=operation)
    action_trace = ActionTrace().append(ActionPhase.SUCCESS, operation=operation)
    trace = interaction_trace(
        InteractionResult(action_state=state, action_trace=action_trace, target="#main")
    )
    assert trace["action_phase"] == "success"
    assert trace["operation_id"] == "op"
    assert trace["generation"] == 3
    assert trace["action_trace"]["schema"] == "hedron.interaction-trace.v1"


def test_async_region_selects_state_slot_and_fallback_markers() -> None:
    output = render(
        AsyncRegion(
            "content",
            state="pending",
            pending="Loading",
            fallback="page",
            label="Results",
        )
    ).html
    assert 'data-hedron-action-phase="pending"' in output
    assert 'data-hedron-async-fallback="page"' in output
    assert 'aria-busy="true"' in output
    assert "Loading" in output
    assert "content" not in output


def test_phase061_surface_contracts_render_closed_markers() -> None:
    bounded = render(Container("form", max_width="sm", align="center", padding="lg")).html
    assert 'data-hedron-max-width="sm"' in bounded
    assert 'data-hedron-align="center"' in bounded
    assert 'data-hedron-padding="lg"' in bounded

    nav = render(NavGroup("Workspace", "Home", "Settings")).html
    assert 'data-hedron-nav-group="true"' in nav
    assert 'aria-label="Workspace"' in nav

    tabs = render(
        Tabs(
            ("Overview", "one"),
            ("History", "two"),
            appearance="underline",
            responsive="scroll",
            density="comfortable",
        )
    ).html
    assert 'data-hedron-appearance="underline"' in tabs
    assert 'data-hedron-responsive="scroll"' in tabs
    assert 'data-hedron-density="comfortable"' in tabs

    ambient = render(AmbientBackdrop("body", pattern="dots", tone="muted")).html
    assert 'data-hedron-ambient-pattern="dots"' in ambient
    assert 'data-hedron-ambient-tone="muted"' in ambient
    assert 'aria-hidden="true"' in ambient


def test_element_markup_starts_with_canonical_action_markers() -> None:
    output = render(ActionAsync("Run")).html
    assert 'data-hedron-action-phase="idle"' in output
    assert 'data-hedron-action-generation="0"' in output
    assert 'aria-busy="false"' in output
