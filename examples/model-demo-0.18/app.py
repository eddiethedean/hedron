"""Minimal model-demo reference app for phase 0.18 exit scenarios."""

from __future__ import annotations

from hedron import Hedron, InteractionRecorder, Text
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
    InferencePriority,
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
REGISTRY.register_action(
    RegisteredAction(
        action_id="classify",
        input_schema={"text": "string"},
        output_schema={"label": "string", "scores": "object"},
        resource_policy="gpu-demo",
        description="Synthetic classifier",
        handler=lambda text: {"label": "cat", "scores": {"cat": 0.9, "dog": 0.1}},
    )
)
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
    ),
    sink=InMemoryFeedbackSink(),
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

RECORDER = InteractionRecorder()
RECORDER.declare_public("POST:/api/predict")


@app.page("/")
def home() -> AppShell:
    queue = POLICY.admit(
        job_type="classify",
        payload={"text": "meow"},
        group="gpu-demo",
        priority=InferencePriority.NORMAL,
    )
    return AppShell(
        nav=(HtmxLink("Demo", "/", target="#main-panel", select="#main-panel", push_url=True),),
        body=MainPanel(
            Text("Model demo (0.18 reference)"),
            Text(f"Interface={INTERFACE.interface_id} source={INTERFACE.source_id}"),
            Text(f"Admission={queue.admission.value} job={queue.job_id}"),
            PredictionLabel(
                [{"class_id": "cat", "score": 0.9, "calibrated": True}],
                title="Synthetic scores",
            ),
            ParameterViewer(
                {"temperature": 0.0, "api_token": "hidden"}, secret_keys=("api_token",)
            ),
            Dialogue([{"speaker": "system", "text": "Synthetic only — no real model."}]),
            Text(f"Examples={EXAMPLES.size} cached={EXAMPLES.get_cached('e1') is not None}"),
            Text(f"Published revision={PUBLISHED.revision_id}"),
            Text(f"Editor rows={len(WORKFLOW.editor_view().rows)}"),
        ),
    )


@app.component("/api/predict", methods=["POST"])
def predict_public() -> Text:
    RECORDER.record(
        method="POST",
        path="/api/predict",
        body={"text": "meow", "password": "should-redact"},
        session_assumptions=("optional demo session",),
    )
    return Text("ok")


def recorded_snippets() -> list[str]:
    return [s.content for s in RECORDER.snippets()]
