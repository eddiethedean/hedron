"""Hugging Face vendor nodes and bounded Space client helpers."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from hedron_gradio.errors import GradioRemoteError
from hedron_gradio.policy import GradioRemoteConfig, normalize_host, redact_sensitive_text

HuggingFaceKind = Literal["model", "dataset", "space", "oauth", "zerogpu"]

_HF_HOSTS = frozenset(
    {
        "huggingface.co",
        "hf.space",
    }
)


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


def hf_space_base_url(space_ref: str) -> str:
    ref = space_ref.strip().strip("/")
    if not ref or ".." in ref or ref.startswith("/"):
        raise GradioRemoteError(f"Invalid Hugging Face Space ref: {space_ref!r}")
    if "/" not in ref:
        raise GradioRemoteError(f"Space ref must be owner/name: {space_ref!r}")
    owner, name = ref.split("/", 1)
    if not owner or not name:
        raise GradioRemoteError(f"Invalid Hugging Face Space ref: {space_ref!r}")
    return f"https://{owner}-{name}.hf.space"


def hf_remote_config_for_space(
    space_ref: str,
    *,
    extra_hosts: frozenset[str] | None = None,
) -> GradioRemoteConfig:
    base_url = hf_space_base_url(space_ref)
    hosts = set(_HF_HOSTS)
    parsed_host = normalize_host(base_url.split("//", 1)[1].split("/", 1)[0])
    hosts.add(parsed_host)
    if extra_hosts:
        hosts.update(normalize_host(item) for item in extra_hosts)
    return GradioRemoteConfig(
        base_url=base_url,
        allowed_hosts=frozenset(hosts),
        allowed_schemes=frozenset({"https"}),
    )


def translate_hf_vendor_status(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Map recorded HF queue/cold-start/quota fixtures to adapter-friendly status."""
    status = str(raw.get("status") or "unknown").lower()
    if status in {"queued", "queue", "starting", "cold_start"}:
        return {"status": "pending", "detail": redact_sensitive_text(str(raw.get("detail", "")))}
    if status in {"failed", "error", "quota", "outage"}:
        message = redact_sensitive_text(str(raw.get("message") or raw.get("detail") or status))
        return {"status": "failed", "error": message}
    if status in {"complete", "ok", "success"}:
        result = raw.get("result")
        if isinstance(result, dict):
            return {"status": "complete", "result": result}
        return {"status": "complete", "result": {"value": result}}
    return {"status": status, "detail": redact_sensitive_text(json.dumps(raw, default=str))}


def load_hf_fixture(name: str) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[4] / "tests" / "fixtures" / "gradio"
    path = root / name
    if not path.is_file():
        raise GradioRemoteError(f"Missing HF fixture: {name}")
    return json.loads(path.read_text(encoding="utf-8"))
