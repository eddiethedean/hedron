"""Portable phase 0.63 trace/profile evidence."""

from __future__ import annotations

import pytest

from hedron_core import (
    ActionTrace,
    OperationIdentity,
    decode_interaction_trace,
    encode_interaction_trace,
    profile_interaction_trace,
)


def test_trace_encoding_is_redacted_bounded_and_deterministic() -> None:
    trace = ActionTrace().append(
        "pending",
        operation=OperationIdentity("op-1", target="#results"),
        facts={"password": "do-not-retain", "component": "Table"},
    )

    first = encode_interaction_trace(trace)
    second = encode_interaction_trace(trace)

    assert first == second
    decoded = decode_interaction_trace(first)
    assert decoded["events"][0]["facts"]["password"] == "[redacted]"
    assert decoded["events"][0]["facts"]["component"] == "Table"


def test_trace_profile_discards_payloads_and_marks_truncation() -> None:
    trace = ActionTrace(max_events=4)
    for index in range(4):
        trace = trace.append("pending", facts={"value": "x" * 200, "index": index})

    encoded = encode_interaction_trace(trace, max_bytes=512)
    profile = profile_interaction_trace(encoded)

    assert profile["schema"] == "hedron.interaction-profile/1"
    assert profile["payloads_retained"] is False
    assert profile["truncated"] is True


def test_trace_decoder_fails_closed_for_unknown_versions() -> None:
    with pytest.raises(ValueError, match="unsupported interaction trace schema"):
        decode_interaction_trace('{"schema":"hedron.interaction-trace.v2","events":[]}')
