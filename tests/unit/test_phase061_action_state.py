"""Phase 0.61 lifecycle and surface contract coverage."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from hedron_core import (
    ActionPhase,
    ActionPolicy,
    ActionState,
    ActionTrace,
    AmbientBackdrop,
    AsyncRegion,
    Container,
    Form,
    Hx,
    InteractionResult,
    NavGroup,
    OperationIdentity,
    Tabs,
    complete_operation,
    render,
)
from hedron_core.action_state import ActionTransitionError, begin_operation, transition_action
from hedron_core.htmx.headers import interaction_trace
from hedron_core.jobs import JobState, JobStatus, action_state_for_job, job_status_interaction
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


def test_retry_policy_is_enforced_and_identity_mismatches_are_stale() -> None:
    operation = OperationIdentity("save-1", target="#editor", revision=4)
    failed, accepted = complete_operation(
        begin_operation(ActionState(), operation)[0],
        ActionPhase.ERROR,
        operation,
        retryable=True,
    )
    assert accepted
    unchanged, accepted = begin_operation(failed, operation.next_generation())
    assert not accepted and unchanged == failed

    retry_policy = ActionPolicy(allow_retry=True, max_attempts=2, idempotent=True)
    pending, accepted = begin_operation(
        failed,
        operation.next_generation(),
        policy=retry_policy,
    )
    assert accepted
    wrong_target = OperationIdentity("save-1", generation=1, target="#other", revision=4)
    unchanged, accepted = complete_operation(pending, ActionPhase.SUCCESS, wrong_target)
    assert not accepted and unchanged == pending
    wrong_revision = OperationIdentity("save-1", generation=1, target="#editor", revision=3)
    unchanged, accepted = complete_operation(pending, ActionPhase.SUCCESS, wrong_revision)
    assert not accepted and unchanged == pending

    no_cancel = ActionPolicy(allow_cancellation=False)
    unchanged, accepted = complete_operation(
        pending,
        ActionPhase.CANCELLED,
        pending.operation,
        policy=no_cancel,
    )
    assert not accepted and unchanged == pending


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


@pytest.mark.parametrize(
    "job_state,phase",
    (
        (JobState.QUEUED, ActionPhase.PENDING),
        (JobState.RUNNING, ActionPhase.PENDING),
        (JobState.SUCCEEDED, ActionPhase.SUCCESS),
        (JobState.FAILED, ActionPhase.ERROR),
        (JobState.CANCELLED, ActionPhase.CANCELLED),
    ),
)
def test_job_status_projects_the_unified_lifecycle(
    job_state: JobState,
    phase: ActionPhase,
) -> None:
    status = JobStatus(
        job_id="job-1",
        state=job_state,
        job_type="report",
        error="failed" if job_state is JobState.FAILED else None,
    )
    state = action_state_for_job(status)
    assert state.phase is phase
    result = job_status_interaction(status)
    assert result.action_state == state
    assert result.action_trace is not None
    assert 'data-hedron-action-phase="' + phase.value + '"' in render(result.content).html


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


@pytest.mark.parametrize(
    "state,slot",
    (
        ("idle", "initial"),
        ("pending", "pending"),
        ("empty", "empty"),
        ("success", "success"),
        ("error", "error"),
        ("timeout", "timeout"),
        ("cancelled", "cancelled"),
        ("stale", "stale"),
        ("conflict", "conflict"),
    ),
)
def test_async_region_covers_each_declared_state(state: str, slot: str | None) -> None:
    kwargs = {
        name: name
        for name in (
            "initial",
            "pending",
            "empty",
            "success",
            "error",
            "timeout",
            "cancelled",
            "stale",
            "retry",
            "conflict",
        )
    }
    output = render(AsyncRegion("ordinary", state=state, **kwargs)).html
    assert f'data-hedron-action-phase="{state}"' in output
    assert (slot if slot is not None else "ordinary") in output


def test_element_state_machine_rejects_late_replaced_result() -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    module = (
        Path(__file__).resolve().parents[2]
        / "packages/hedron-elements/src/hedron_elements/static/interaction-state.mjs"
    )
    script = f"""
const {{ InteractionState }} = await import({module.as_uri()!r});
const machine = new InteractionState({{ policy: "replace" }});
if (!machine.begin("first")) throw new Error("first operation was dropped");
const firstGeneration = machine.generation;
if (!machine.begin("second")) throw new Error("replacement was dropped");
if (machine.complete("success", {{
  operationId: "first",
  generation: firstGeneration,
}})) throw new Error("stale result accepted");
if (!machine.complete("success", {{
  operationId: "second",
  generation: machine.generation,
}})) throw new Error("current result rejected");
if (machine.state !== "success") throw new Error("wrong terminal state");
"""
    result = subprocess.run(
        [node, "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


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

    for stylesheet in (
        "packages/hedron-core/src/hedron_core/static/hedron-default.css",
        "packages/hedron/src/hedron/static/hedron-default.css",
    ):
        css = Path(stylesheet).read_text(encoding="utf-8")
        assert ".hedron-identity-text" in css
        assert "forced-colors: active" in css


def test_element_markup_starts_with_canonical_action_markers() -> None:
    output = render(ActionAsync("Run")).html
    assert 'data-hedron-action-phase="idle"' in output
    assert 'data-hedron-action-generation="0"' in output
    assert 'aria-busy="false"' in output


def test_htmx_form_busy_boundary_starts_with_action_lifecycle_markers() -> None:
    output = render(Form("fields", action="/save", hx=Hx(busy="region"))).html
    assert 'data-hedron-busy="region"' in output
    assert 'data-hedron-action-phase="idle"' in output
    assert 'data-hedron-action-generation="0"' in output
