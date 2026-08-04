"""Live transport backpressure budgets."""

from __future__ import annotations

from hedron_core.channel import PageSessionChannel, RegionUpdate
from hedron_core.streaming import ChunkedList, StreamBudget, TokenStream


def test_stream_budget_caps_chars() -> None:
    stream = TokenStream(
        tokens=["x" * 100] * 100,
        region_id="t",
        budget=StreamBudget(max_chunks=1000, max_chars=250, deadline_seconds=None),
    )
    out = "".join(stream.iter_chunks())
    assert len(out) <= 250


def test_channel_message_budget() -> None:
    from hedron_core.channel import ChannelBudget

    channel = PageSessionChannel(
        channel_id="c",
        declared_regions=frozenset({"r"}),
        budget=ChannelBudget(max_messages=2, max_message_bytes=1000, max_batch=10),
    )
    channel.encode_region_update(RegionUpdate("r", "a"))
    channel.encode_region_update(RegionUpdate("r", "b"))
    try:
        channel.encode_region_update(RegionUpdate("r", "c"))
        raised = False
    except RuntimeError:
        raised = True
    assert raised


def test_chunked_list_deadline_none_still_caps() -> None:
    source = ChunkedList(
        ["a"] * 50,
        region_id="x",
        item_html=lambda item, i: item,
        budget=StreamBudget(max_chunks=5, deadline_seconds=None),
    )
    assert len(list(source.iter_chunks())) == 5
