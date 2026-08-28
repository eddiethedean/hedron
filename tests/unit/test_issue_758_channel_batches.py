"""Regression coverage for atomic channel batch accounting (#758)."""

from __future__ import annotations

import pytest

from hedron_core.channel import ChannelBudget, PageSessionChannel, RegionUpdate


def _channel() -> PageSessionChannel:
    return PageSessionChannel(
        channel_id="c",
        declared_regions=frozenset({"r"}),
        budget=ChannelBudget(max_messages=2, max_message_bytes=4, max_batch=2),
    )


@pytest.mark.parametrize(
    "invalid",
    [
        RegionUpdate("r", "too-long"),
        RegionUpdate("missing", "ok"),
        RegionUpdate("r", "ok", swap="javascript:bad"),
    ],
)
def test_failed_batch_does_not_consume_message_budget(invalid: RegionUpdate) -> None:
    channel = _channel()
    with pytest.raises(ValueError):
        channel.batch_updates([RegionUpdate("r", "ok"), invalid])
    assert channel.messages_sent == 0

    messages = channel.batch_updates([RegionUpdate("r", "a"), RegionUpdate("r", "b")])
    assert len(messages) == 2
    assert channel.messages_sent == 2


def test_batch_budget_failure_is_atomic() -> None:
    channel = _channel()
    channel.encode_region_update(RegionUpdate("r", "four"))
    with pytest.raises(RuntimeError, match="budget exhausted"):
        channel.batch_updates([RegionUpdate("r", "a"), RegionUpdate("r", "b")])
    assert channel.messages_sent == 1


def test_empty_batch_preserves_message_budget() -> None:
    channel = _channel()
    assert channel.batch_updates([]) == []
    assert channel.messages_sent == 0


def test_batch_validates_count_and_utf8_bytes_without_consuming_budget() -> None:
    channel = _channel()

    with pytest.raises(ValueError, match="max_batch"):
        channel.batch_updates(
            [RegionUpdate("r", "a"), RegionUpdate("r", "b"), RegionUpdate("r", "c")]
        )
    assert channel.messages_sent == 0

    # Two code points occupy four bytes; adding one more must fail the byte limit.
    with pytest.raises(ValueError, match="max_message_bytes"):
        channel.batch_updates([RegionUpdate("r", "ééé")])
    assert channel.messages_sent == 0
