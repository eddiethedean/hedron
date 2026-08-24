"""Phase 0.62 navigation, failure, identity, and optimistic-core contracts."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from starlette.requests import Request
from starlette.responses import Response

from hedron import (
    FailureBoundary,
    FailureDisposition,
    IdentityRegistry,
    IdentityTarget,
    NavigationMachine,
    NavigationPhase,
    NavigationPolicy,
    StateTransfer,
    StateTransferPolicy,
    apply_navigation_headers,
    evaluate_prefetch_request,
)
from hedron_core.action_state import OperationIdentity
from hedron_data import OptimisticMutation


def test_navigation_machine_rejects_late_generation() -> None:
    machine = NavigationMachine()
    first = machine.start(navigation_id="first", url="/first")
    second = machine.start(navigation_id="second", url="/second")

    stale = machine.commit(first, title="First")
    assert not stale.accepted
    assert stale.diagnostic_code == "HED-NAV-0005"
    assert machine.state.phase is NavigationPhase.PENDING

    committed = machine.commit(second, title="Second", focus_target="#main")
    assert committed.accepted
    assert machine.state.phase is NavigationPhase.COMMITTED
    assert machine.state.title == "Second"


def test_navigation_policy_bounds_prefetch_and_safe_urls() -> None:
    policy = NavigationPolicy(prefetch_enabled=True)
    allowed = policy
    assert allowed.prefetch_max_bytes == 262_144
    from hedron_core.navigation import decide_prefetch

    assert decide_prefetch(policy, method="GET", url="/next", origin="https://example.test").allowed
    assert (
        decide_prefetch(policy, method="POST", url="/next", origin="https://example.test").reason
        == "unsafe_method"
    )
    assert (
        decide_prefetch(
            policy, method="GET", url="https://evil.test", origin="https://example.test"
        ).reason
        == "unsafe_origin"
    )
    assert (
        decide_prefetch(
            policy, method="GET", url="/next", origin="https://example.test", private=True
        ).reason
        == "private_response"
    )


def test_failure_boundary_localizes_errors_and_reconciles_unknown_results() -> None:
    boundary = FailureBoundary("panel", "#panel", max_retries=1)
    operation = OperationIdentity("refresh", target="#panel")
    pending = boundary.start(operation)
    assert pending.accepted
    failed = pending.boundary.complete(operation, success=False, retryable=True)
    assert failed.disposition is FailureDisposition.LOCAL
    retried = failed.boundary.retry(operation)
    assert retried.accepted
    unknown = retried.boundary.complete(
        retried.boundary.operation or operation,
        success=False,
        uncertain=True,
    )
    assert unknown.disposition is FailureDisposition.RECONCILE
    assert unknown.diagnostic_code == "HED-FAILURE-0004"


def test_missing_fallback_propagates() -> None:
    boundary = FailureBoundary("shell", "#shell", has_fallback=False)
    decision = boundary.start(OperationIdentity("navigation", target="#shell"))
    assert not decision.accepted
    assert decision.disposition is FailureDisposition.PROPAGATE
    assert decision.diagnostic_code == "HED-FAILURE-0001"


def test_identity_registry_rejects_duplicate_writers_and_bounds_transfer() -> None:
    registry = IdentityRegistry(StateTransferPolicy(max_fields=1, max_bytes=100))
    target = IdentityTarget("user", "#identity", "server", "1")
    registry.register(target)
    with pytest.raises(Exception, match="Duplicate state writer"):
        registry.register(IdentityTarget("user", "#identity", "browser", "1"))
    transfer = StateTransfer(target, {"display": "Ada"}, revision=3)
    assert registry.transfer(transfer).fields["display"] == "Ada"
    with pytest.raises(Exception, match="field limit"):
        registry.transfer(StateTransfer(target, {"a": 1, "b": 2}))


def test_phase062_optimistic_core_requires_revision_and_uses_approved_risks() -> None:
    mutation = OptimisticMutation.from_reversible_toggle(
        action_id="favorite",
        row_key="item-1",
        field="favorite",
        value=True,
        previous=False,
        base_revision=4,
    )
    assert mutation.phase062_ready
    mutation.propose().submit().unknown()
    assert mutation.state.value == "unknown"
    mutation.resolve_with_refetch(server_revision=5)
    assert mutation.state.value == "refetched"

    with pytest.raises(ValueError, match="base revision"):
        OptimisticMutation.from_cell_edits(
            action_id="edit",
            base_revision=None,
            patches=[{"row_key": "r", "field": "name", "value": "Ada"}],
        ).validate_phase062()


def test_navigation_response_headers_and_prefetch_request() -> None:
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "https",
        "path": "/next",
        "raw_path": b"/next",
        "query_string": b"",
        "headers": [(b"host", b"example.test")],
        "client": ("127.0.0.1", 1),
        "server": ("example.test", 443),
    }
    request = Request(scope)
    policy = NavigationPolicy(prefetch_enabled=True)
    assert evaluate_prefetch_request(request, policy).allowed
    identity = NavigationMachine().start(navigation_id="n", url="/next")
    response = apply_navigation_headers(Response("ok"), identity=identity, title="Next")
    assert response.headers["X-Hedron-Navigation-Generation"] == "0"
    assert response.headers["X-Hedron-Title"] == "Next"


def test_browser_navigation_controller_rejects_stale_results() -> None:
    module = (
        Path(__file__).resolve().parents[2]
        / "packages/hedron-elements/src/hedron_elements/static/navigation-062.mjs"
    )
    script = f"""
      import {{ NavigationController, decidePrefetch, runViewTransition }} from {module.as_uri()!r};
      const controller = new NavigationController();
      const first = controller.start('/first', {{ navigationId: 'first' }});
      const second = controller.start('/second', {{ navigationId: 'second' }});
      if (controller.commit(first).accepted) throw new Error('stale navigation committed');
      if (!controller.commit(second).accepted) throw new Error('current navigation rejected');
      const prefetch = decidePrefetch({{ enabled: true, method: 'POST', url: '/x',
        origin: 'https://example.test' }});
      if (prefetch.reason !== 'unsafe_method') {{
        throw new Error('unsafe prefetch allowed');
      }}
      let updated = false;
      await runViewTransition(() => {{ updated = true; }}, {{ documentRoot: {{}}, enabled: true }});
      if (!updated) throw new Error('feature-absent transition path did not update');
    """
    subprocess.run(["node", "--input-type=module", "-e", script], check=True)
