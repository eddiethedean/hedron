"""Phase 0.18 WORKFLOW-018: InferenceWorkflow authz and adversarial suites."""

from __future__ import annotations

import pytest

from hedron_core import (
    ActionRegistry,
    InferencePolicy,
    InferenceWorkflow,
    RegisteredAction,
    WorkflowError,
    WorkflowNode,
    WorkflowNodeKind,
    WorkflowPermission,
    WorkflowPort,
)
from hedron_core.codes import HED_WORKFLOW_0001, HED_WORKFLOW_0002, HED_WORKFLOW_0003


def _ports(*specs: tuple[str, str, str]) -> tuple[WorkflowPort, ...]:
    return tuple(
        WorkflowPort(port_id=pid, name=pid, type_name=typ, direction=direction)
        for pid, typ, direction in specs
    )


def test_workflow_validate_publish_rollback() -> None:
    wf = InferenceWorkflow(workflow_id="demo", tenant_id="t1")
    wf.grant("alice", WorkflowPermission.EDIT, WorkflowPermission.PUBLISH, WorkflowPermission.RUN)
    wf.add_node(
        WorkflowNode(
            node_id="in",
            kind=WorkflowNodeKind.INPUT,
            label="Input",
            ports=_ports(("out", "text", "out")),
        ),
        principal="alice",
    )
    wf.add_node(
        WorkflowNode(
            node_id="model",
            kind=WorkflowNodeKind.MODEL,
            label="Classify",
            action_id="classify",
            ports=_ports(("in", "text", "in"), ("out", "label", "out")),
        ),
        principal="alice",
    )
    wf.add_node(
        WorkflowNode(
            node_id="out",
            kind=WorkflowNodeKind.OUTPUT,
            label="Out",
            ports=_ports(("in", "label", "in")),
        ),
        principal="alice",
    )
    wf.connect(from_node="in", from_port="out", to_node="model", to_port="in", principal="alice")
    wf.connect(from_node="model", from_port="out", to_node="out", to_port="in", principal="alice")
    assert wf.topological_order() == ["in", "model", "out"]

    rev = wf.publish(principal="alice")
    assert rev.immutable
    view = wf.editor_view(mode="table")
    assert view.mode == "table"
    assert any(row.get("node_id") == "model" for row in view.rows)

    wf.add_node(
        WorkflowNode(
            node_id="extra",
            kind=WorkflowNodeKind.REFERENCE,
            label="Ref",
            ports=_ports(("out", "text", "out")),
        ),
        principal="alice",
    )
    wf.rollback(rev.revision_id, principal="alice")
    ids = {n["node_id"] for n in wf.to_json()["nodes"]}
    assert "extra" not in ids
    assert "model" in ids


def test_cycle_authz_and_adversarial() -> None:
    wf = InferenceWorkflow(workflow_id="bad")
    wf.grant("ed", WorkflowPermission.EDIT)
    wf.add_node(
        WorkflowNode(
            node_id="a",
            kind=WorkflowNodeKind.INPUT,
            label="A",
            ports=_ports(("out", "t", "out"), ("in", "t", "in")),
        ),
        principal="ed",
    )
    wf.add_node(
        WorkflowNode(
            node_id="b",
            kind=WorkflowNodeKind.OUTPUT,
            label="B",
            ports=_ports(("out", "t", "out"), ("in", "t", "in")),
        ),
        principal="ed",
    )
    wf.connect(from_node="a", from_port="out", to_node="b", to_port="in", principal="ed")
    with pytest.raises(WorkflowError) as exc:
        wf.connect(from_node="b", from_port="out", to_node="a", to_port="in", principal="ed")
    assert exc.value.code == HED_WORKFLOW_0001
    # Cyclic edge must not remain after rejection.
    assert ("b", "out", "a", "in") not in wf._edges
    assert len(wf._edges) == 1

    with pytest.raises(WorkflowError) as exc2:
        wf.publish(principal="ed")
    assert exc2.value.code == HED_WORKFLOW_0002

    with pytest.raises(WorkflowError) as exc3:
        wf.add_node(
            WorkflowNode(
                node_id="evil",
                kind=WorkflowNodeKind.ACTION,
                label="Evil",
                action_id="x",
                parameters={"host_path": "/etc/passwd"},
                ports=(),
            ),
            principal="ed",
        )
    assert exc3.value.code == HED_WORKFLOW_0003

    wf.grant("ed", WorkflowPermission.PUBLISH)
    with pytest.raises(WorkflowError) as exc4:
        wf.expose_http(principal="ed", enabled=True)
    assert exc4.value.code == HED_WORKFLOW_0003

    # Optimistic conflict
    etag = wf.etag
    wf.optimistic_edit(principal="ed", expected_etag=etag)
    with pytest.raises(WorkflowError) as exc5:
        wf.optimistic_edit(principal="ed", expected_etag=etag - 1)
    assert exc5.value.code == HED_WORKFLOW_0002


def test_from_json_rejects_model_without_action_id() -> None:
    wf = InferenceWorkflow(workflow_id="import")
    wf.grant("ed", WorkflowPermission.EDIT)
    with pytest.raises(WorkflowError) as exc:
        wf.from_json(
            {
                "nodes": [
                    {
                        "node_id": "m",
                        "kind": "model",
                        "label": "M",
                        "action_id": None,
                        "ports": [],
                    }
                ],
                "edges": [],
            },
            principal="ed",
            replace=True,
        )
    assert exc.value.code == HED_WORKFLOW_0001
    assert wf.to_json()["nodes"] == []


def test_workflow_run_executes_registered_action() -> None:
    registry = ActionRegistry()
    registry.register_action(
        RegisteredAction(
            action_id="classify",
            input_schema={"text": "string"},
            output_schema={"label": "string"},
            resource_policy="gpu",
            handler=lambda text: {"label": f"pred:{text}"},
        )
    )
    wf = InferenceWorkflow(workflow_id="run-demo")
    wf.grant("alice", WorkflowPermission.EDIT, WorkflowPermission.RUN)
    wf.add_node(
        WorkflowNode(
            node_id="in",
            kind=WorkflowNodeKind.INPUT,
            label="Input",
            ports=_ports(("out", "text", "out")),
        ),
        principal="alice",
    )
    wf.add_node(
        WorkflowNode(
            node_id="model",
            kind=WorkflowNodeKind.MODEL,
            label="Classify",
            action_id="classify",
            ports=_ports(("text", "text", "in"), ("out", "label", "out")),
        ),
        principal="alice",
    )
    wf.add_node(
        WorkflowNode(
            node_id="out",
            kind=WorkflowNodeKind.OUTPUT,
            label="Out",
            ports=_ports(("in", "label", "in")),
        ),
        principal="alice",
    )
    wf.connect(from_node="in", from_port="out", to_node="model", to_port="text", principal="alice")
    wf.connect(from_node="model", from_port="out", to_node="out", to_port="in", principal="alice")

    result = wf.run(
        principal="alice",
        registry=registry,
        inputs={"in": {"out": "meow"}},
    )
    assert result.status == "completed"
    assert result.outputs["out"]["in"]["label"] == "pred:meow"

    with pytest.raises(WorkflowError) as exc:
        wf.run(principal="bob", registry=registry, inputs={})
    assert exc.value.code == HED_WORKFLOW_0002


def test_workflow_run_honors_cancel() -> None:
    registry = ActionRegistry()
    registry.register_action(
        RegisteredAction(
            action_id="slow",
            input_schema={"x": "string"},
            output_schema={"y": "string"},
            resource_policy="gpu",
            authorization_required=False,
            handler=lambda **_: {"y": "done"},
        )
    )
    policy = InferencePolicy()
    policy._mark_cancel_id("req-1")
    wf = InferenceWorkflow(workflow_id="cancel-demo")
    wf.grant("alice", WorkflowPermission.EDIT, WorkflowPermission.RUN)
    wf.add_node(
        WorkflowNode(
            node_id="m",
            kind=WorkflowNodeKind.ACTION,
            label="A",
            action_id="slow",
            ports=(),
        ),
        principal="alice",
    )
    result = wf.run(
        principal="alice",
        registry=registry,
        policy=policy,
        request_id="req-1",
    )
    assert result.status == "cancelled"
    assert result.nodes[0].status == "cancelled"
