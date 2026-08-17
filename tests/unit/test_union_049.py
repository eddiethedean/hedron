"""UNION-049 tagged public-wire kinds."""

from __future__ import annotations

import json
from pathlib import Path

from hedron_core.channel import ChannelMessage
from hedron_core.diagnostics import HedronError
from hedron_core.jobs.types import JobState, JobStatus
from hedron_core.wire_unions import (
    PUBLIC_WIRE_DISCRIMINATOR,
    PUBLIC_WIRE_SYMBOLS,
    unknown_kind,
    warn_smart_union,
    wire_envelope,
)
from hedron_data.events import GridCellEvent


def test_exact_symbol_families_are_locked() -> None:
    assert PUBLIC_WIRE_SYMBOLS["outcome_map_results"]
    assert "Patch" in PUBLIC_WIRE_SYMBOLS["typed_updates"]
    assert "GridCellEvent" in PUBLIC_WIRE_SYMBOLS["selected_event_envelopes"]
    assert "JobStatus" in PUBLIC_WIRE_SYMBOLS["job_messages"]
    assert "McpTool" in PUBLIC_WIRE_SYMBOLS["mcp_envelopes"]
    assert "GradioEndpoint" in PUBLIC_WIRE_SYMBOLS["remote_adapter_descriptors"]


def test_existing_kinds_and_unknown_fail_closed() -> None:
    event = GridCellEvent(row_key="1")
    assert getattr(event, PUBLIC_WIRE_DISCRIMINATOR) == "cell"
    message = ChannelMessage(kind="ping")
    assert message.kind == "ping"
    envelope = wire_envelope("job-status", {"state": JobState.QUEUED.value, "job_id": "1"})
    assert envelope["kind"] == "job-status"
    _ = JobStatus(job_id="1", state=JobState.QUEUED, job_type="demo")
    try:
        unknown_kind("nope", allowed=("cell", "ping"))
    except HedronError as exc:
        assert exc.diagnostic.code == "HED-FP-0004"
    else:
        raise AssertionError("unknown kind")


def test_untagged_application_models_warn_only_on_public_catalog() -> None:
    assert warn_smart_union(include_in_schema=False, has_kind=False) is None
    assert warn_smart_union(include_in_schema=True, has_kind=False) == "public-catalog-smart-union"
    assert warn_smart_union(include_in_schema=True, has_kind=True) is None


def test_cross_runtime_tagged_wire_fixture() -> None:
    fixture = Path("packages/hedron-runtime-node/fixtures/tagged_wire_049.json")
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    assert payload["discriminator"] == PUBLIC_WIRE_DISCRIMINATOR
    allowed = tuple(example["kind"] for example in payload["examples"])
    for example in payload["examples"]:
        unknown_kind(example["kind"], allowed=allowed)


def test_cross_runtime_union_fixtures_exist() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    for rel in (
        "packages/hedron-runtime-node/fixtures/portable_unions_v1.json",
        "packages/hedron-runtime-java/fixtures/portable_unions_v1.json",
    ):
        assert (root / rel).is_file()
