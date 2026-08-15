"""Model demo composition, examples, and governed feedback (RFC-0045 / RFC-0046)."""

from __future__ import annotations

from hedron_core.model_demo.actions import (
    ActionRegistry,
    ModelDemoError,
    RegisteredAction,
    RegisteredCallableAdapter,
)
from hedron_core.model_demo.examples import CachedExampleResult, ExampleItem, ExampleSet
from hedron_core.model_demo.feedback import (
    FeedbackPolicy,
    FeedbackRecord,
    FeedbackSink,
    PredictionFeedback,
)
from hedron_core.model_demo.feedback import (
    InMemoryFeedbackSink as InMemoryFeedbackSink,
)
from hedron_core.model_demo.surface import InferenceInterface, ModelDemo

__all__ = [
    "CachedExampleResult",
    "ExampleItem",
    "ExampleSet",
    "FeedbackPolicy",
    "FeedbackRecord",
    "FeedbackSink",
    "InferenceInterface",
    "ModelDemo",
    "ModelDemoError",
    "PredictionFeedback",
    "RegisteredAction",
    "RegisteredCallableAdapter",
    "ActionRegistry",
]
