"""Hugging Face vendor nodes as thin workflow adapters (no Hub calls)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

HuggingFaceKind = Literal["model", "dataset", "space", "oauth", "zerogpu"]


@dataclass(frozen=True)
class HuggingFaceVendorNode:
    node_id: str
    kind: HuggingFaceKind
    ref: str

    def to_workflow_node(self) -> dict[str, str]:
        workflow_kind = "dataset" if self.kind == "dataset" else "remote"
        action_id = f"hf:{self.kind}:{self.ref}"
        return {
            "id": self.node_id,
            "kind": workflow_kind,
            "action_id": action_id,
            "ref": self.ref,
        }


def hf_space_node(node_id: str, space_ref: str) -> HuggingFaceVendorNode:
    return HuggingFaceVendorNode(node_id=node_id, kind="space", ref=space_ref)
