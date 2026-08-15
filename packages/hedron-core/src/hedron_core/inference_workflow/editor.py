"""Structured list/outline/table editor over a workflow graph."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from hedron_core.inference_workflow.graph import WorkflowEditorView, WorkflowNode


def editor_view(
    nodes: Mapping[str, WorkflowNode],
    edges: list[tuple[str, str, str, str]],
    *,
    mode: str = "table",
) -> WorkflowEditorView:
    rows: list[Mapping[str, Any]] = []
    for node in nodes.values():
        rows.append(
            {
                "node_id": node.node_id,
                "kind": node.kind.value,
                "label": node.label,
                "action_id": node.action_id,
                "ports": [p.port_id for p in node.ports],
                "parameters": dict(node.parameters),
            }
        )
    for frm, fp, to, tp in edges:
        rows.append(
            {
                "connection": f"{frm}.{fp} -> {to}.{tp}",
                "from_node": frm,
                "to_node": to,
            }
        )
    return WorkflowEditorView(mode=mode, rows=tuple(rows))
