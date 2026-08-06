"""Versioned permissioned inference workflows (RFC-0050 / WORKFLOW-018).

Graph JSON cannot execute arbitrary Python, install packages, access host paths,
or automatically create HTTP/MCP endpoints. A structured list/outline/table editor
exposes nodes without requiring a visual canvas.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from hedron_core.codes import HED_WORKFLOW_0001, HED_WORKFLOW_0002, HED_WORKFLOW_0003
from hedron_core.diagnostics import HedronError, error
from hedron_core.typing_aliases import JsonValue

__all__ = [
    "InferenceWorkflow",
    "PublishedRevision",
    "WorkflowEditorView",
    "WorkflowError",
    "WorkflowNode",
    "WorkflowNodeKind",
    "WorkflowPermission",
    "WorkflowPort",
]


class WorkflowError(ValueError):
    """Workflow validation, authorization, or adversarial failure."""

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        diagnostic: HedronError | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.diagnostic = diagnostic


class WorkflowNodeKind(StrEnum):
    REFERENCE = "reference"
    INPUT = "input"
    ACTION = "action"
    MODEL = "model"
    REMOTE = "remote"
    DATASET = "dataset"
    ARTIFACT = "artifact"
    OUTPUT = "output"


class WorkflowPermission(StrEnum):
    READ = "read"
    RUN = "run"
    EDIT = "edit"
    PUBLISH = "publish"


@dataclass(frozen=True, slots=True)
class WorkflowPort:
    port_id: str
    name: str
    type_name: str
    direction: str  # "in" | "out"


@dataclass(frozen=True, slots=True)
class WorkflowNode:
    node_id: str
    kind: WorkflowNodeKind
    label: str
    ports: tuple[WorkflowPort, ...] = ()
    action_id: str | None = None
    parameters: Mapping[str, JsonValue] = field(default_factory=dict)
    secret_refs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PublishedRevision:
    revision_id: str
    version: int
    published_at: float
    publisher: str
    immutable: bool = True
    snapshot: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class WorkflowEditorView:
    """Non-spatial structured editor: list / outline / table rows."""

    mode: str  # "list" | "outline" | "table"
    rows: tuple[Mapping[str, Any], ...]


_FORBIDDEN_PARAM_KEYS = frozenset(
    {
        "python",
        "code",
        "eval",
        "exec",
        "host_path",
        "file_path",
        "cwd",
        "install",
        "pip",
        "shell",
    }
)


@dataclass
class InferenceWorkflow:
    """Typed, versioned inference DAG with separate read/run/edit/publish authority."""

    workflow_id: str
    schema_version: str = "1"
    tenant_id: str | None = None
    _nodes: dict[str, WorkflowNode] = field(default_factory=dict, init=False)
    _edges: list[tuple[str, str, str, str]] = field(default_factory=list, init=False)
    # (from_node, from_port, to_node, to_port)
    _permissions: dict[str, set[WorkflowPermission]] = field(default_factory=dict, init=False)
    _published: list[PublishedRevision] = field(default_factory=list, init=False)
    _history: list[Mapping[str, Any]] = field(default_factory=list, init=False)
    _version: int = field(default=1, init=False)
    _etag: int = field(default=1, init=False)
    _http_exposed: bool = field(default=False, init=False)
    _mcp_exposed: bool = field(default=False, init=False)

    def grant(self, principal: str, *permissions: WorkflowPermission) -> None:
        self._permissions.setdefault(principal, set()).update(permissions)

    def assert_permission(self, principal: str, permission: WorkflowPermission) -> None:
        allowed = self._permissions.get(principal, set())
        if permission not in allowed:
            raise WorkflowError(
                f"Principal {principal!r} lacks {permission.value}",
                code=HED_WORKFLOW_0002,
                diagnostic=error(
                    HED_WORKFLOW_0002,
                    title="Workflow authorization failure",
                    explanation=f"Missing permission {permission.value}.",
                    remediation="Grant the required permission explicitly.",
                ),
            )

    def add_node(self, node: WorkflowNode, *, principal: str) -> None:
        self.assert_permission(principal, WorkflowPermission.EDIT)
        self._reject_forbidden_parameters(node.parameters)
        if node.node_id in self._nodes:
            raise WorkflowError(
                f"Duplicate node id: {node.node_id!r}",
                code=HED_WORKFLOW_0001,
            )
        if node.kind in {WorkflowNodeKind.ACTION, WorkflowNodeKind.MODEL} and not node.action_id:
            raise WorkflowError(
                "Action/model nodes require action_id",
                code=HED_WORKFLOW_0001,
                diagnostic=error(
                    HED_WORKFLOW_0001,
                    title="Missing action binding",
                    explanation="Operator nodes must map to an explicit registered action.",
                    remediation="Set action_id to a registered action.",
                ),
            )
        self._nodes[node.node_id] = node
        self._bump()

    def connect(
        self,
        *,
        from_node: str,
        from_port: str,
        to_node: str,
        to_port: str,
        principal: str,
    ) -> None:
        self.assert_permission(principal, WorkflowPermission.EDIT)
        if from_node not in self._nodes or to_node not in self._nodes:
            raise WorkflowError("Unknown node in connection", code=HED_WORKFLOW_0001)
        src = self._port(from_node, from_port, "out")
        dst = self._port(to_node, to_port, "in")
        if src.type_name != dst.type_name:
            raise WorkflowError(
                f"Port type mismatch: {src.type_name} -> {dst.type_name}",
                code=HED_WORKFLOW_0001,
            )
        self._edges.append((from_node, from_port, to_node, to_port))
        self.validate()
        self._bump()

    def validate(self) -> None:
        # Cycle detection via DFS
        adj: dict[str, list[str]] = defaultdict(list)
        for frm, _, to, _ in self._edges:
            adj[frm].append(to)
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node_id: str) -> None:
            if node_id in visiting:
                raise WorkflowError(
                    "Cycle detected in workflow graph",
                    code=HED_WORKFLOW_0001,
                    diagnostic=error(
                        HED_WORKFLOW_0001,
                        title="Workflow cycle",
                        explanation="Cycles are rejected at validation time.",
                        remediation="Remove the cyclic edge.",
                    ),
                )
            if node_id in visited:
                return
            visiting.add(node_id)
            for nxt in adj[node_id]:
                visit(nxt)
            visiting.remove(node_id)
            visited.add(node_id)

        for node_id in self._nodes:
            visit(node_id)

    def topological_order(self) -> list[str]:
        self.validate()
        indeg: dict[str, int] = {n: 0 for n in self._nodes}
        adj: dict[str, list[str]] = defaultdict(list)
        for frm, _, to, _ in self._edges:
            adj[frm].append(to)
            indeg[to] += 1
        queue = deque([n for n, d in indeg.items() if d == 0])
        order: list[str] = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for nxt in adj[node]:
                indeg[nxt] -= 1
                if indeg[nxt] == 0:
                    queue.append(nxt)
        if len(order) != len(self._nodes):
            raise WorkflowError("Cycle detected", code=HED_WORKFLOW_0001)
        return order

    def publish(self, *, principal: str) -> PublishedRevision:
        self.assert_permission(principal, WorkflowPermission.PUBLISH)
        snapshot = self.to_json()
        rev = PublishedRevision(
            revision_id=f"{self.workflow_id}-r{self._version}",
            version=self._version,
            published_at=time.time(),
            publisher=principal,
            immutable=True,
            snapshot=snapshot,
        )
        self._published.append(rev)
        self._history.append({"op": "publish", "revision": rev.revision_id})
        return rev

    def rollback(self, revision_id: str, *, principal: str) -> None:
        self.assert_permission(principal, WorkflowPermission.EDIT)
        match = next((r for r in self._published if r.revision_id == revision_id), None)
        if match is None:
            raise WorkflowError("Unknown revision", code=HED_WORKFLOW_0002)
        self.from_json(match.snapshot, principal=principal, replace=True)
        self._history.append({"op": "rollback", "revision": revision_id})

    def optimistic_edit(self, *, principal: str, expected_etag: int) -> None:
        self.assert_permission(principal, WorkflowPermission.EDIT)
        if expected_etag != self._etag:
            raise WorkflowError(
                "Optimistic concurrency conflict",
                code=HED_WORKFLOW_0002,
                diagnostic=error(
                    HED_WORKFLOW_0002,
                    title="Edit conflict",
                    explanation=f"Expected etag {expected_etag}, have {self._etag}.",
                    remediation="Reload and retry the edit.",
                ),
            )

    def expose_http(self, *, principal: str, enabled: bool) -> None:
        """HTTP exposure is never automatic — requires explicit publish+permission."""
        self.assert_permission(principal, WorkflowPermission.PUBLISH)
        if enabled and not self._published:
            raise WorkflowError(
                "Cannot expose HTTP before publish",
                code=HED_WORKFLOW_0003,
                diagnostic=error(
                    HED_WORKFLOW_0003,
                    title="Auto-exposure forbidden",
                    explanation="Graphs cannot auto-create HTTP endpoints.",
                    remediation="Publish an immutable revision, then expose explicitly.",
                ),
            )
        self._http_exposed = enabled

    def expose_mcp(self, *, principal: str, enabled: bool) -> None:
        self.assert_permission(principal, WorkflowPermission.PUBLISH)
        if enabled and not self._published:
            raise WorkflowError(
                "Cannot expose MCP before publish",
                code=HED_WORKFLOW_0003,
            )
        self._mcp_exposed = enabled

    @property
    def http_exposed(self) -> bool:
        return self._http_exposed

    @property
    def mcp_exposed(self) -> bool:
        return self._mcp_exposed

    @property
    def etag(self) -> int:
        return self._etag

    @property
    def published_revisions(self) -> tuple[PublishedRevision, ...]:
        return tuple(self._published)

    def editor_view(self, *, mode: str = "table") -> WorkflowEditorView:
        rows: list[Mapping[str, Any]] = []
        for node in self._nodes.values():
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
        for frm, fp, to, tp in self._edges:
            rows.append(
                {
                    "connection": f"{frm}.{fp} -> {to}.{tp}",
                    "from_node": frm,
                    "to_node": to,
                }
            )
        return WorkflowEditorView(mode=mode, rows=tuple(rows))

    def to_json(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "schema_version": self.schema_version,
            "tenant_id": self.tenant_id,
            "version": self._version,
            "etag": self._etag,
            "nodes": [
                {
                    "node_id": n.node_id,
                    "kind": n.kind.value,
                    "label": n.label,
                    "action_id": n.action_id,
                    "parameters": dict(n.parameters),
                    "secret_refs": list(n.secret_refs),
                    "ports": [
                        {
                            "port_id": p.port_id,
                            "name": p.name,
                            "type_name": p.type_name,
                            "direction": p.direction,
                        }
                        for p in n.ports
                    ],
                }
                for n in self._nodes.values()
            ],
            "edges": [
                {
                    "from_node": a,
                    "from_port": b,
                    "to_node": c,
                    "to_port": d,
                }
                for a, b, c, d in self._edges
            ],
            "http_exposed": False,  # never serialize exposure as auto-on
            "mcp_exposed": False,
        }

    def from_json(self, data: Mapping[str, Any], *, principal: str, replace: bool = False) -> None:
        self.assert_permission(principal, WorkflowPermission.EDIT)
        raw = dict(data)
        # Adversarial: reject host paths / code in JSON
        blob = str(raw)
        for forbidden in ("/etc/", "C:\\", "eval(", "exec(", "__import__"):
            if forbidden in blob:
                raise WorkflowError(
                    "Forbidden host path or code in workflow JSON",
                    code=HED_WORKFLOW_0003,
                    diagnostic=error(
                        HED_WORKFLOW_0003,
                        title="Adversarial workflow payload",
                        explanation="Graph JSON must not embed host paths or code.",
                        remediation="Use registered actions and secret references only.",
                    ),
                )
        if replace:
            self._nodes.clear()
            self._edges.clear()
        for node_data in raw.get("nodes", []):
            params = dict(node_data.get("parameters") or {})
            self._reject_forbidden_parameters(params)
            node = WorkflowNode(
                node_id=str(node_data["node_id"]),
                kind=WorkflowNodeKind(str(node_data["kind"])),
                label=str(node_data.get("label", "")),
                action_id=node_data.get("action_id"),
                parameters=params,
                secret_refs=tuple(node_data.get("secret_refs") or ()),
                ports=tuple(
                    WorkflowPort(
                        port_id=str(p["port_id"]),
                        name=str(p.get("name", p["port_id"])),
                        type_name=str(p.get("type_name", "any")),
                        direction=str(p.get("direction", "in")),
                    )
                    for p in node_data.get("ports") or ()
                ),
            )
            self._nodes[node.node_id] = node
        for edge in raw.get("edges", []):
            self._edges.append(
                (
                    str(edge["from_node"]),
                    str(edge["from_port"]),
                    str(edge["to_node"]),
                    str(edge["to_port"]),
                )
            )
        self.validate()
        self._bump()

    def migrate_schema(self, target_version: str) -> None:
        # Identity migration for v1; future versions append transforms here.
        if self.schema_version == target_version:
            return
        if self.schema_version == "1" and target_version == "1":
            return
        # Accept forward identity for documented versions only
        allowed = {"1"}
        if target_version not in allowed:
            raise WorkflowError(
                f"Unsupported schema migration to {target_version}",
                code=HED_WORKFLOW_0001,
            )
        self.schema_version = target_version
        self._bump()

    def _port(self, node_id: str, port_id: str, direction: str) -> WorkflowPort:
        node = self._nodes[node_id]
        for port in node.ports:
            if port.port_id == port_id and port.direction == direction:
                return port
        raise WorkflowError(
            f"Missing {direction} port {port_id!r} on {node_id!r}",
            code=HED_WORKFLOW_0001,
        )

    def _reject_forbidden_parameters(self, parameters: Mapping[str, JsonValue]) -> None:
        for key in parameters:
            lowered = key.lower()
            if lowered in _FORBIDDEN_PARAM_KEYS or any(
                tok in lowered for tok in ("path", "code", "eval", "exec", "shell")
            ):
                raise WorkflowError(
                    f"Forbidden parameter key: {key!r}",
                    code=HED_WORKFLOW_0003,
                    diagnostic=error(
                        HED_WORKFLOW_0003,
                        title="Forbidden workflow parameter",
                        explanation="Parameters cannot encode host code or paths.",
                        remediation="Pass data values only; bind code via registered actions.",
                    ),
                )

    def _bump(self) -> None:
        self._version += 1
        self._etag += 1
        self._history.append({"op": "edit", "version": self._version, "etag": self._etag})
