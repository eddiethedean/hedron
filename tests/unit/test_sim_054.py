"""SIM-054 evidence: declared subset/divergence manifest, recording, and bounds."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest

from hedron_conformance.authoring_loop import HED_SIM_LIMIT, HED_SIM_UNSUPPORTED
from hedron_sim import (
    MANIFEST_CATEGORIES,
    SIM_MANIFEST_SCHEMA,
    SIM_SCENARIO_SCHEMA,
    SimClock,
    SimLimitError,
    SimLimits,
    SimRecorder,
    SimScenario,
    UnsupportedSimFeatureError,
    divergence_manifest,
    export_scenario,
    import_scenario,
    manifest_entry,
    manifest_markdown,
    require_supported_feature,
    require_supported_method,
    subset_manifest,
)
from hedron_sim.recording import HED_SIM_LIMIT as SIM_LIMIT_CODE
from hedron_sim.subset import HED_SIM_UNSUPPORTED as SIM_UNSUPPORTED_CODE

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_CATEGORIES = (
    "methods",
    "attrs",
    "swaps",
    "history",
    "forms",
    "extensions",
    "errors",
    "timing",
)


def test_sim_054_packet_bound() -> None:
    gate = tomllib.loads(
        (ROOT / "docs" / "acceptance" / "release-gate-0.54.toml").read_text(encoding="utf-8")
    )
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["SIM-054"]["command"] == "python scripts/check_sim_054.py"
    assert rows["SIM-054"]["owner"] == "hedron-sim"
    locks = tomllib.loads(
        (ROOT / "docs" / "acceptance" / "authoring-sim-notebook-054.toml").read_text(
            encoding="utf-8"
        )
    )
    assert locks["simulator"]["silent_unsupported"] is False
    assert sorted(locks["simulator"]["limits"]) == ["byte", "depth", "step", "time"]


def test_failure_codes_match_shared_schema() -> None:
    assert SIM_UNSUPPORTED_CODE == HED_SIM_UNSUPPORTED
    assert SIM_LIMIT_CODE == HED_SIM_LIMIT
    assert UnsupportedSimFeatureError.code == HED_SIM_UNSUPPORTED
    assert SimLimitError.code == HED_SIM_LIMIT


def test_subset_manifest_covers_every_declared_category() -> None:
    manifest = subset_manifest()
    assert manifest["schema_version"] == SIM_MANIFEST_SCHEMA
    categories = manifest["categories"]
    for name in REQUIRED_CATEGORIES:
        assert name in categories, name
    assert "GET" in categories["methods"]
    assert "hx-get" in categories["attrs"]
    assert "innerHTML" in categories["swaps"]
    # Machine-readable: the whole manifest must round-trip through JSON.
    assert json.loads(json.dumps(manifest)) == manifest


def test_divergence_manifest_marks_unsupported_explicitly() -> None:
    manifest = divergence_manifest()
    assert manifest["failure_code"] == HED_SIM_UNSUPPORTED
    categories = manifest["categories"]
    assert set(categories) == set(MANIFEST_CATEGORIES)
    for name in REQUIRED_CATEGORIES:
        unsupported = categories[name]["unsupported"]
        assert unsupported, f"{name} declares no divergence"
        for row in unsupported:
            assert row["supported"] is False
            assert row["failure_code"] == HED_SIM_UNSUPPORTED
            assert row["note"], row
    assert "pushState" in [row["name"] for row in categories["history"]["unsupported"]]
    assert "hx-ext" in [row["name"] for row in categories["extensions"]["unsupported"]]
    assert json.loads(json.dumps(manifest)) == manifest


def test_unsupported_feature_fails_visibly() -> None:
    with pytest.raises(UnsupportedSimFeatureError) as excinfo:
        require_supported_feature("history", "pushState")
    assert excinfo.value.code == HED_SIM_UNSUPPORTED
    assert excinfo.value.category == "history"
    assert excinfo.value.feature == "pushState"

    with pytest.raises(UnsupportedSimFeatureError):
        require_supported_feature("attrs", "hx-boost")
    with pytest.raises(UnsupportedSimFeatureError):
        require_supported_feature("attrs", "hx-nonexistent")
    with pytest.raises(UnsupportedSimFeatureError):
        require_supported_feature("teleportation", "anything")

    assert require_supported_feature("methods", "GET") == "GET"
    assert require_supported_method("post") == "POST"


def test_manifest_entry_and_markdown() -> None:
    entry = manifest_entry("swaps", "innerHTML")
    assert entry is not None
    assert entry.supported is True
    assert entry.failure_code is None
    assert manifest_entry("swaps", "morph") is not None
    assert manifest_entry("swaps", "nope") is None

    text = manifest_markdown()
    assert SIM_MANIFEST_SCHEMA in text
    assert HED_SIM_UNSUPPORTED in text
    for name in REQUIRED_CATEGORIES:
        assert f"## {name}" in text


def test_recorder_captures_requests_swaps_triggers_delays_failures() -> None:
    recorder = SimRecorder("notes-demo")
    recorder.record_trigger("click", selector="#add")
    recorder.record_request("POST", "/notes", target="#list", status=200)
    recorder.record_delay(120)
    recorder.record_swap("beforeend", target="#list")
    recorder.record_failure(HED_SIM_UNSUPPORTED, "hx-boost is not emulated")

    scenario = recorder.scenario()
    assert scenario.scenario_id == "notes-demo"
    assert [event.kind for event in scenario.events] == [
        "trigger",
        "request",
        "delay",
        "swap",
        "failure",
    ]
    assert scenario.duration_ms == 120
    assert scenario.of_kind("request")[0].detail["method"] == "POST"
    # Virtual time only moves when the scenario says so.
    assert [event.at_ms for event in scenario.events] == [0, 0, 120, 120, 120]


def test_recorder_rejects_unsupported_method_and_swap() -> None:
    recorder = SimRecorder()
    with pytest.raises(UnsupportedSimFeatureError):
        recorder.record_request("TRACE", "/x")
    with pytest.raises(UnsupportedSimFeatureError):
        recorder.record_swap("morphdom", target="#out")
    assert recorder.events == ()


def test_scenario_export_import_round_trip() -> None:
    recorder = SimRecorder("round-trip")
    recorder.record_request("GET", "/fragment", target="#out")
    recorder.record_delay(50)
    recorder.record_swap("innerHTML", target="#out")
    scenario = recorder.scenario()

    text = export_scenario(scenario, indent=2)
    assert json.loads(text)["schema_version"] == SIM_SCENARIO_SCHEMA
    assert import_scenario(text) == scenario
    assert import_scenario(text.encode("utf-8")) == scenario
    assert import_scenario(scenario.as_dict()) == scenario
    # Export is deterministic, so a recording diffs cleanly against a fixture.
    assert export_scenario(import_scenario(text)) == export_scenario(scenario)


def test_scenario_import_rejects_version_and_shape_skew() -> None:
    payload = SimRecorder("skew").scenario().as_dict()
    with pytest.raises(ValueError, match="schema_version"):
        import_scenario({**payload, "schema_version": "hedron-sim-scenario-0"})
    with pytest.raises(ValueError, match="event kind"):
        import_scenario({**payload, "events": [{"kind": "teleport", "name": "x"}]})
    with pytest.raises(ValueError, match="mapping"):
        import_scenario({**payload, "events": ["not-an-event"]})


def test_clock_advances_only_forward_and_honors_time_limit() -> None:
    clock = SimClock(limits=SimLimits(max_time_ms=500))
    assert clock.advance(200) == 200
    assert clock.advance(0) == 200
    with pytest.raises(ValueError, match="non-negative"):
        clock.advance(-1)
    with pytest.raises(SimLimitError) as excinfo:
        clock.advance(400)
    assert excinfo.value.code == HED_SIM_LIMIT
    assert excinfo.value.limit == "max_time_ms"
    assert clock.now_ms == 200
    clock.reset()
    assert clock.now_ms == 0


def test_limits_bound_bytes_steps_and_depth() -> None:
    steps = SimRecorder(limits=SimLimits(max_steps=2))
    steps.record_trigger("click")
    steps.record_trigger("click")
    with pytest.raises(SimLimitError) as step_error:
        steps.record_trigger("click")
    assert step_error.value.limit == "max_steps"

    nested = {
        "schema_version": SIM_SCENARIO_SCHEMA,
        "scenario_id": "deep",
        "limits": {"max_depth": 2},
        "events": [
            {"kind": "request", "name": "GET /x", "detail": {"a": {"b": {"c": "deep"}}}},
        ],
    }
    with pytest.raises(SimLimitError) as depth_error:
        import_scenario(nested)
    assert depth_error.value.limit == "max_depth"

    scenario = SimScenario(scenario_id="big", limits=SimLimits(max_bytes=32))
    with pytest.raises(SimLimitError) as byte_error:
        export_scenario(scenario)
    assert byte_error.value.limit == "max_bytes"
    assert byte_error.value.code == HED_SIM_LIMIT

    with pytest.raises(SimLimitError):
        import_scenario(export_scenario(SimRecorder("x").scenario()), limits=SimLimits(max_bytes=8))


def test_deep_mapping_import_fails_with_typed_depth_limit() -> None:
    detail: dict[str, object] = {}
    for _ in range(1_100):
        detail = {"child": detail}
    payload = {
        "schema_version": SIM_SCENARIO_SCHEMA,
        "scenario_id": "deep",
        "events": [
            {"kind": "failure", "name": "deep", "at_ms": 0, "detail": detail},
        ],
    }
    with pytest.raises(SimLimitError) as excinfo:
        import_scenario(payload)
    assert excinfo.value.limit == "max_depth"
    assert excinfo.value.code == HED_SIM_LIMIT


def test_deep_json_import_translates_parser_recursion_failure() -> None:
    detail = '{"child":' * 1_100 + "{}" + "}" * 1_100
    payload = (
        '{"schema_version":"hedron-sim-scenario-1","scenario_id":"deep","events":'
        '[{"kind":"failure","name":"deep","at_ms":0,"detail":' + detail + "}]}"
    )
    with pytest.raises(SimLimitError) as excinfo:
        import_scenario(payload)
    assert excinfo.value.limit == "max_depth"


@pytest.mark.parametrize("at_ms", [-1, -500])
def test_scenario_import_rejects_negative_timestamps(at_ms: int) -> None:
    payload = {
        "schema_version": SIM_SCENARIO_SCHEMA,
        "scenario_id": "negative",
        "events": [
            {"kind": "delay", "name": "bad", "at_ms": at_ms, "detail": {"ms": 0}},
        ],
    }
    with pytest.raises(SimLimitError) as excinfo:
        import_scenario(payload)
    assert excinfo.value.limit == "max_time_ms"
    assert excinfo.value.value == at_ms


@pytest.mark.parametrize("at_ms", [-0.5, -0.1, True, 1.9, "1"])
def test_scenario_import_rejects_non_integer_timestamps(at_ms: object) -> None:
    payload = {
        "schema_version": SIM_SCENARIO_SCHEMA,
        "scenario_id": "invalid-time",
        "events": [
            {"kind": "delay", "name": "bad", "at_ms": at_ms, "detail": {"ms": 0}},
        ],
    }
    with pytest.raises(ValueError, match="at_ms must be an integer"):
        import_scenario(payload)
