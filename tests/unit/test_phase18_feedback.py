"""Phase 0.18 FEEDBACK-018: PredictionFeedback consent and retention."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from hedron_core import (
    FeedbackPolicy,
    InMemoryFeedbackSink,
    ModelDemoError,
    PredictionFeedback,
)
from hedron_core.codes import HED_FEEDBACK_0001


def test_feedback_requires_consent_and_redacts() -> None:
    with pytest.raises(ModelDemoError) as exc:
        FeedbackPolicy(collection_notice="", tenant_id="t1").validate()
    assert exc.value.code == HED_FEEDBACK_0001

    with pytest.raises(ModelDemoError):
        FeedbackPolicy(
            collection_notice="We collect ratings",
            tenant_id="t1",
            treat_as_ground_truth=True,
        ).validate()

    policy = FeedbackPolicy(
        collection_notice="We collect ratings with consent",
        tenant_id="tenant-a",
        redaction_fields=("secret",),
        allow_export=True,
    )
    fb = PredictionFeedback(policy=policy, sink=InMemoryFeedbackSink())
    with pytest.raises(ModelDemoError, match="disabled"):
        fb.submit(rating=1, consented=True, principal="alice")

    with pytest.raises(ModelDemoError, match="consent"):
        fb.enable(consented=False)

    fb.enable(consented=True)
    with pytest.raises(ModelDemoError, match="principal"):
        fb.submit(rating=5, consented=True)

    record = fb.submit(
        rating=5,
        label="good",
        reason="clear",
        correction="cat",
        input_refs=("in-1",),
        output_refs=("out-1",),
        consented=True,
        payload={"secret": "x", "ok": "y"},
        principal="alice",
    )
    assert record.redacted["secret"] == "[redacted]"
    assert record.redacted["ok"] == "y"
    assert record.tenant_id == "tenant-a"
    exported = fb.export(principal="alice")
    assert len(exported) == 1
    assert fb.delete(record.record_id, principal="alice") is True


def test_feedback_retention_and_abuse_controls() -> None:
    policy = FeedbackPolicy(
        collection_notice="notice",
        tenant_id="t1",
        allow_export=True,
        retention_seconds=0.001,
        abuse_controls=True,
    )
    fb = PredictionFeedback(policy=policy, sink=InMemoryFeedbackSink(), max_text_chars=8)
    fb.enable(consented=True)
    record = fb.submit(
        rating=1,
        consented=True,
        principal="alice",
        now=1000.0,
    )
    assert record.record_id
    # Later export past retention should purge.
    assert list(fb.export(principal="alice", now=1000.1)) == []

    fb2 = PredictionFeedback(policy=policy, sink=InMemoryFeedbackSink(), max_text_chars=8)
    fb2.enable(consented=True)
    with pytest.raises(ModelDemoError, match="max_text_chars"):
        fb2.submit(
            rating=1,
            reason="this is way too long",
            consented=True,
            principal="alice",
        )


def test_feedback_shared_sink_is_tenant_scoped() -> None:
    sink = InMemoryFeedbackSink()
    first = PredictionFeedback(
        policy=FeedbackPolicy(collection_notice="notice", tenant_id="tenant-a", allow_export=True),
        sink=sink,
    )
    second = PredictionFeedback(
        policy=FeedbackPolicy(collection_notice="notice", tenant_id="tenant-b", allow_export=True),
        sink=sink,
    )
    first.enable(consented=True)
    second.enable(consented=True)
    a = first.submit(rating=1, consented=True, principal="alice")
    b = second.submit(rating=2, consented=True, principal="bob")
    assert a.record_id != b.record_id
    assert [record.tenant_id for record in first.export(principal="alice")] == ["tenant-a"]
    assert [record.tenant_id for record in second.export(principal="bob")] == ["tenant-b"]
    assert first.delete(b.record_id, principal="alice") is False
    assert second.delete(b.record_id, principal="bob") is True


def test_feedback_retention_and_capacity_are_tenant_scoped() -> None:
    sink = InMemoryFeedbackSink()
    expired = PredictionFeedback(
        policy=FeedbackPolicy(
            collection_notice="notice",
            tenant_id="tenant-a",
            allow_export=True,
            retention_seconds=1,
        ),
        sink=sink,
        max_records=1,
    )
    current = PredictionFeedback(
        policy=FeedbackPolicy(
            collection_notice="notice",
            tenant_id="tenant-b",
            allow_export=True,
            retention_seconds=1000,
        ),
        sink=sink,
        max_records=1,
    )
    expired.enable(consented=True)
    current.enable(consented=True)
    expired.submit(consented=True, principal="alice", now=1)
    kept = current.submit(consented=True, principal="bob", now=100)
    assert expired.export(principal="alice", now=100) == ()
    assert current.export(principal="bob", now=100) == (kept,)
    with pytest.raises(ModelDemoError, match="store full"):
        current.submit(consented=True, principal="bob", now=101)


def test_feedback_concurrent_shared_sink_ids_do_not_collide() -> None:
    sink = InMemoryFeedbackSink()
    collector = PredictionFeedback(
        policy=FeedbackPolicy(
            collection_notice="notice",
            tenant_id="tenant-a",
            allow_export=True,
            abuse_controls=False,
        ),
        sink=sink,
        max_records=200,
    )
    collector.enable(consented=True)
    with ThreadPoolExecutor(max_workers=8) as pool:
        records = tuple(
            pool.map(
                lambda index: collector.submit(label=str(index), consented=True, principal="alice"),
                range(100),
            )
        )
    assert len({record.record_id for record in records}) == 100
    assert len(collector.export(principal="alice")) == 100
