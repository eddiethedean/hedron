"""Hugging Face vendor nodes as thin workflow adapters (no Hub calls)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

HuggingFaceKind = Literal["model", "dataset", "space", "oauth", "zerogpu"]


@dataclass(frozen=True)
class HuggingFaceVendorNode:
    node_id: str
    kind: HuggingFaceKind
    ref: str

    def to_workflow_node(self) -> dict[str, Any]:
        """Emit InferenceWorkflow-compatible node JSON (node_id/label/ports)."""
        workflow_kind = "dataset" if self.kind == "dataset" else "remote"
        action_id = f"hf:{self.kind}:{self.ref}"
        return {
            "node_id": self.node_id,
            "kind": workflow_kind,
            "label": f"HF {self.kind}: {self.ref}",
            "action_id": action_id,
            "parameters": {"ref": self.ref},
            "secret_refs": (),
            "ports": (
                {
                    "port_id": "in",
                    "name": "in",
                    "type_name": "any",
                    "direction": "in",
                },
                {
                    "port_id": "out",
                    "name": "out",
                    "type_name": "any",
                    "direction": "out",
                },
            ),
            "ref": self.ref,
        }


def hf_space_node(node_id: str, space_ref: str) -> HuggingFaceVendorNode:
    return HuggingFaceVendorNode(node_id=node_id, kind="space", ref=space_ref)
