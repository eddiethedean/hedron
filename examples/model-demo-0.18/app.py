"""Interactive synthetic classifier showing Hedron's governed model-demo APIs."""

from __future__ import annotations

from typing import Annotated

from fastapi import Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from hedron import (
    Control,
    FormBody,
    Hedron,
    InteractionRecorder,
    Text,
)
from hedron_core import (
    ActionRegistry,
    AppShell,
    ConcurrencyGroup,
    Dialogue,
    ExampleItem,
    ExampleSet,
    FeedbackPolicy,
    HtmxLink,
    InferencePolicy,
    InferenceWorkflow,
    InMemoryFeedbackSink,
    MainPanel,
    ModelDemo,
    ParameterViewer,
    PredictionFeedback,
    PredictionLabel,
    RegisteredAction,
    WorkflowNode,
    WorkflowNodeKind,
    WorkflowPermission,
    WorkflowPort,
)
from hedron_core.jobs import InMemoryJobBackend, set_job_backend

set_job_backend(InMemoryJobBackend())

app = Hedron(
    title="Model demo 0.18", explorer="off", security="standard", session_secret="dev-only"
)

REGISTRY = ActionRegistry()


def classify_text(text: str) -> dict[str, object]:
    """Deterministic local classifier: useful for UI learning, not a real model."""
    normalized = text.casefold()
    cat_score = 0.9 if any(word in normalized for word in ("cat", "meow", "kitten")) else 0.2
    dog_score = round(1.0 - cat_score, 2)
    return {
        "label": "cat" if cat_score >= dog_score else "dog",
        "scores": {"cat": cat_score, "dog": dog_score},
    }


CLASSIFY_ACTION = RegisteredAction(
    action_id="classify",
    input_schema={"text": "string"},
    output_schema={"label": "string", "scores": "object"},
    resource_policy="gpu-demo",
    description="Deterministic synthetic classifier",
    handler=classify_text,
)
REGISTRY.register_action(CLASSIFY_ACTION)
DEMO = ModelDemo(registry=REGISTRY)
INTERFACE = DEMO.build_from_action("classify")

EXAMPLES = ExampleSet(set_id="synth", action_id="classify")
EXAMPLES.add(
    ExampleItem(example_id="e1", label="meow", inputs={"text": "meow"}, provenance="synthetic")
)
EXAMPLES.store_result("e1", {"label": "cat"}, cost_units=0.01)

POLICY = InferencePolicy(groups={"gpu-demo": ConcurrencyGroup(name="gpu-demo", limit=2)})
FEEDBACK = PredictionFeedback(
    policy=FeedbackPolicy(
        collection_notice="Ratings are optional and require consent.",
        tenant_id="demo",
        redaction_fields=("secret",),
        allow_export=True,
    ),
    sink=InMemoryFeedbackSink(),
)
FEEDBACK.enable(consented=True)
FEEDBACK.submit(
    rating=5,
    label="helpful",
    reason="clear",
    consented=True,
    principal="demo",
    payload={"secret": "x", "note": "ok"},
)

WORKFLOW = InferenceWorkflow(workflow_id="classify-flow", tenant_id="demo")
WORKFLOW.grant("demo", WorkflowPermission.EDIT, WorkflowPermission.PUBLISH, WorkflowPermission.RUN)
WORKFLOW.add_node(
    WorkflowNode(
        node_id="in",
        kind=WorkflowNodeKind.INPUT,
        label="Text",
        ports=(WorkflowPort("out", "out", "text", "out"),),
    ),
    principal="demo",
)
WORKFLOW.add_node(
    WorkflowNode(
        node_id="model",
        kind=WorkflowNodeKind.MODEL,
        label="Classify",
        action_id="classify",
        ports=(
            WorkflowPort("in", "in", "text", "in"),
            WorkflowPort("out", "out", "label", "out"),
        ),
    ),
    principal="demo",
)
WORKFLOW.add_node(
    WorkflowNode(
        node_id="out",
        kind=WorkflowNodeKind.OUTPUT,
        label="Label",
        ports=(WorkflowPort("in", "in", "label", "in"),),
    ),
    principal="demo",
)
WORKFLOW.connect(from_node="in", from_port="out", to_node="model", to_port="in", principal="demo")
WORKFLOW.connect(from_node="model", from_port="out", to_node="out", to_port="in", principal="demo")
PUBLISHED = WORKFLOW.publish(principal="demo")
RUN = WORKFLOW.run(
    principal="demo",
    registry=REGISTRY,
    inputs={"in": {"out": "meow"}},
)

RECORDER = InteractionRecorder()
RECORDER.declare_public("POST:/predict")
RECORDER.record(
    method="POST",
    path="/predict",
    body={"text": "meow", "password": "should-redact"},
    session_assumptions=("optional demo session",),
)


class ClassifyIn(BaseModel):
    text: Annotated[
        str,
        Field(min_length=1, max_length=500),
        Control(kind="textarea", label="Text"),
    ]


@app.action("/predict", fallback="/")
def predict_public(request: Request, data: Annotated[ClassifyIn, FormBody()]):
    handler = CLASSIFY_ACTION.handler
    if handler is None:  # Defensive: registered demos fail closed without a handler.
        raise RuntimeError("classify action has no handler")
    result = handler(text=data.text)
    request.session["prediction"] = result
    RECORDER.record(
        method="POST",
        path="/predict",
        body={"text": data.text, "password": "should-redact"},
        session_assumptions=("optional demo session",),
    )
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@app.page("/")
def home(request: Request) -> AppShell:
    # Show policy groups without admitting on every GET (avoids slot leak).
    groups = ", ".join(POLICY.groups)
    feedback_count = len(FEEDBACK.export(principal="demo"))
    prediction = request.session.get("prediction")
    scores = prediction.get("scores", {}) if isinstance(prediction, dict) else {}
    score_rows = [
        {"class_id": str(label), "score": float(score), "calibrated": False}
        for label, score in scores.items()
        if isinstance(score, (int, float))
    ]
    prediction_panel = (
        PredictionLabel(score_rows, title=f"Prediction: {prediction['label']}")
        if isinstance(prediction, dict) and score_rows
        else Text("Submit text to generate a synthetic prediction.")
    )
    return AppShell(
        nav=(HtmxLink("Demo", "/", target="#main-panel", select="#main-panel", push_url=True),),
        body=MainPanel(
            Text("Model demo (0.18 reference)"),
            Text("Try “meow at the window” or “walk the dog”. This runs locally."),
            predict_public.form(
                submit_label="Classify",
                value=ClassifyIn(text="meow at the window"),
            ),
            prediction_panel,
            Text(f"Interface={INTERFACE.interface_id} source={INTERFACE.source_id}"),
            Text(f"Policy groups={groups}"),
            Text(f"Workflow run={RUN.status} outputs={RUN.outputs}"),
            ParameterViewer(
                {"temperature": 0.0, "api_token": "hidden"}, secret_keys=("api_token",)
            ),
            Dialogue([{"speaker": "system", "text": "Synthetic only — no real model."}]),
            Text(f"Examples={EXAMPLES.size} cached={EXAMPLES.get_cached('e1') is not None}"),
            Text(f"Feedback records={feedback_count}"),
            Text(f"Published revision={PUBLISHED.revision_id}"),
            Text(f"Editor rows={len(WORKFLOW.editor_view().rows)}"),
            Text(f"Recorder snippets={len(RECORDER.snippets())}"),
        ),
    )


def recorded_snippets() -> list[str]:
    return [s.content for s in RECORDER.snippets()]
