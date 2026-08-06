"""Phase 0.18 FEEDBACK-018: PredictionFeedback consent and retention."""

from __future__ import annotations

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
        fb.submit(rating=1, consented=True)

    with pytest.raises(ModelDemoError, match="consent"):
        fb.enable(consented=False)

    fb.enable(consented=True)
    record = fb.submit(
        rating=5,
        label="good",
        reason="clear",
        correction="cat",
        input_refs=("in-1",),
        output_refs=("out-1",),
        consented=True,
        payload={"secret": "x", "ok": "y"},
    )
    assert record.redacted["secret"] == "[redacted]"
    assert record.redacted["ok"] == "y"
    assert record.tenant_id == "tenant-a"
    exported = fb.export()
    assert len(exported) == 1
    assert fb.delete(record.record_id) is True
