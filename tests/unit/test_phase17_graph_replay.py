"""Phase 0.17 REPLAY-017: interaction-graph recorder and deterministic replay."""

from __future__ import annotations

import os

import pytest

from hedron_core import (
    DashboardBinding,
    GraphRecording,
    InteractionGraph,
    record_exchange,
    replay,
)
from hedron_core.codes import HED_GRAPH_0006, HED_PATCH_0002


def _graph_with_binding() -> InteractionGraph:
    graph = InteractionGraph()
    graph.declare_inputs("chart.click")
    graph.register(
        DashboardBinding(
            id="xf",
            triggers=("chart.click",),
            snapshot_inputs=(),
            targets=("detail",),
            action_id="filter_detail",
        )
    )
    return graph


def test_record_exchange_redacts_secrets() -> None:
    recording = GraphRecording()
    event = record_exchange(
        recording,
        correlation_id="c-1",
        binding_id="xf",
        kind="trigger",
        payload={
            "regions": {"detail": {"value": 1}},
            "password": "hunter2",
            "token": "abc",
            "secret": "s",
            "authorization": "Bearer x",
            "safe": "ok",
        },
    )
    assert event.payload["password"] == "[redacted]"
    assert event.payload["token"] == "[redacted]"
    assert event.payload["secret"] == "[redacted]"
    assert event.payload["authorization"] == "[redacted]"
    assert event.payload["safe"] == "ok"
    assert len(recording.events) == 1


def test_replay_applies_trigger_and_patch() -> None:
    graph = _graph_with_binding()
    recording = GraphRecording(initial_regions={"detail": {"_version": 1, "value": 0, "items": []}})
    record_exchange(
        recording,
        correlation_id="c-1",
        binding_id="xf",
        kind="trigger",
        payload={"regions": {"detail": {"_version": 1, "value": 3, "items": []}}},
    )
    record_exchange(
        recording,
        correlation_id="c-2",
        binding_id="xf",
        kind="patch",
        payload={
            "target_id": "detail",
            "path": "value",
            "op": "assign",
            "value": 9,
            "expected_version": 1,
        },
    )

    regions, audit = replay(graph, recording)
    assert regions["detail"]["value"] == 9
    assert [a["kind"] for a in audit] == ["trigger", "patch"]
    assert all(a.get("applied") for a in audit)


def test_replay_schedule_stale_duplicate_disconnect_conflict() -> None:
    graph = _graph_with_binding()
    recording = GraphRecording(initial_regions={"detail": {"_version": 1, "value": 1}})
    record_exchange(
        recording,
        correlation_id="c-1",
        binding_id="xf",
        kind="trigger",
        payload={"regions": {"detail": {"_version": 1, "value": 2}}},
    )

    regions, audit = replay(
        graph,
        recording,
        schedule=["stale", "duplicate", "conflict", "disconnect"],
    )
    assert regions["detail"]["value"] == 2
    kinds = [a["kind"] for a in audit]
    assert kinds == ["trigger", "stale", "duplicate", "conflict", "disconnect"]
    assert audit[-1]["code"] == HED_GRAPH_0006
    assert any(a.get("code") == HED_PATCH_0002 for a in audit if a["kind"] == "conflict")


def test_replay_duplicate_correlation_skips_second_apply() -> None:
    graph = _graph_with_binding()
    recording = GraphRecording(initial_regions={"detail": {"value": 0}})
    record_exchange(
        recording,
        correlation_id="same",
        binding_id="xf",
        kind="trigger",
        payload={"regions": {"detail": {"value": 1}}},
    )
    record_exchange(
        recording,
        correlation_id="same",
        binding_id="xf",
        kind="trigger",
        payload={"regions": {"detail": {"value": 99}}},
    )
    regions, audit = replay(graph, recording)
    assert regions["detail"]["value"] == 1
    assert audit[1]["kind"] == "duplicate"
    assert audit[1]["skipped"] is True


def test_replay_patch_version_conflict_audits_fallback() -> None:
    graph = _graph_with_binding()
    recording = GraphRecording(initial_regions={"detail": {"_version": 5, "value": 1}})
    record_exchange(
        recording,
        correlation_id="c-bad",
        binding_id="xf",
        kind="patch",
        payload={
            "target_id": "detail",
            "path": "value",
            "op": "assign",
            "value": 2,
            "expected_version": 1,
        },
    )
    regions, audit = replay(graph, recording)
    assert regions["detail"]["value"] == 1
    assert audit[0]["kind"] == "conflict"
    assert audit[0]["full_fragment_fallback"] is True
    assert audit[0]["code"] == HED_PATCH_0002


def test_replay_has_no_sleep_dependency() -> None:
    from pathlib import Path

    import hedron_core.dashboard_replay as mod

    source = Path(mod.__file__).read_text(encoding="utf-8")
    assert "time.sleep" not in source
    assert "sleep(" not in source


@pytest.mark.browser
@pytest.mark.skipif(
    os.environ.get("HEDRON_BROWSER") != "1",
    reason="Opt-in: set HEDRON_BROWSER=1 for Playwright smoke",
)
def test_graph_replay_browser_smoke_placeholder() -> None:
    graph = _graph_with_binding()
    recording = GraphRecording(initial_regions={"detail": {"value": 0}})
    record_exchange(
        recording,
        correlation_id="c-1",
        binding_id="xf",
        kind="trigger",
        payload={"regions": {"detail": {"value": 1}}},
    )
    regions, _audit = replay(graph, recording)
    assert regions["detail"]["value"] == 1
