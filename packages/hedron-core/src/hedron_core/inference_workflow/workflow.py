"""Versioned permissioned inference workflows (RFC-0050 / WORKFLOW-018)."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from hedron_core.codes import HED_WORKFLOW_0001, HED_WORKFLOW_0002, HED_WORKFLOW_0003
from hedron_core.diagnostics import error
from hedron_core.inference_workflow.graph import (
    FORBIDDEN_PARAM_KEYS,
    PublishedRevision,
    WorkflowEditorView,
    WorkflowError,
    WorkflowNode,
    WorkflowNodeKind,
    WorkflowNodeResult,
    WorkflowPermission,
    WorkflowPort,
    WorkflowRunResult,
)
from hedron_core.typing_aliases import JsonValue

if TYPE_CHECKING:
    from hedron_core.inference import InferencePolicy
    from hedron_core.model_demo import ActionRegistry


@dataclass
class InferenceWorkflow:
    """Typed, versioned inference DAG with separate read/run/edit/publish authority."""

    workflow_id: str
    schema_version: str = "1"
    tenant_id: str | None = None
    _nodes: dict[str, WorkflowNode] = field(default_factory=dict[str, WorkflowNode], init=False)
    _edges: list[tuple[str, str, str, str]] = field(
        default_factory=list[tuple[str, str, str, str]], init=False
    )
    # (from_node, from_port, to_node, to_port)
    _permissions: dict[str, set[WorkflowPermission]] = field(
        default_factory=dict[str, set[WorkflowPermission]], init=False
    )
    _published: list[PublishedRevision] = field(default_factory=list[PublishedRevision], init=False)
    _history: list[Mapping[str, Any]] = field(default_factory=list[Mapping[str, Any]], init=False)
    _version: int = field(default=1, init=False)
    _etag: int = field(default=1, init=False)
    _http_exposed: bool = field(default=False, init=False)
    _mcp_exposed: bool = field(default=False, init=False)

    def grant(self, principal: str, *permissions: WorkflowPermission) -> None:
        from hedron_core.inference_workflow.authz import grant as _grant

        _grant(self._permissions, principal, *permissions)

    def assert_permission(self, principal: str, permission: WorkflowPermission) -> None:
        from hedron_core.inference_workflow.authz import assert_permission as _assert

        _assert(self._permissions, principal, permission)

    def add_node(self, node: WorkflowNode, *, principal: str) -> None:
        self.assert_permission(principal, WorkflowPermission.EDIT)
        self._insert_node(node)
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
        edge = (from_node, from_port, to_node, to_port)
        self._edges.append(edge)
        try:
            self.validate()
        except WorkflowError:
            self._edges.pop()
            raise
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
        from hedron_core.inference_workflow.editor import editor_view as _editor_view

        return _editor_view(self._nodes, self._edges, mode=mode)

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
        pending_nodes: list[WorkflowNode] = []
        for node_data in raw.get("nodes", []):
            params = dict(node_data.get("parameters") or {})
            node = WorkflowNode(
                node_id=str(node_data["node_id"]),
                kind=WorkflowNodeKind(str(node_data["kind"])),
                label=str(node_data.get("label", node_data["node_id"])),
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
            # Validate before mutating so partial loads cannot leave invalid graphs.
            self._validate_node(node, existing={n.node_id for n in pending_nodes})
            pending_nodes.append(node)
        pending_edges: list[tuple[str, str, str, str]] = []
        for edge in raw.get("edges", []):
            pending_edges.append(
                (
                    str(edge["from_node"]),
                    str(edge["from_port"]),
                    str(edge["to_node"]),
                    str(edge["to_port"]),
                )
            )
        for node in pending_nodes:
            self._nodes[node.node_id] = node
        self._edges.extend(pending_edges)
        try:
            self.validate()
        except WorkflowError:
            if replace:
                self._nodes.clear()
                self._edges.clear()
            else:
                for node in pending_nodes:
                    self._nodes.pop(node.node_id, None)
                del self._edges[-len(pending_edges) :]
            raise
        self._bump()

    def run(
        self,
        *,
        principal: str,
        registry: ActionRegistry,
        inputs: Mapping[str, Any] | None = None,
        policy: InferencePolicy | None = None,
        request_id: str | None = None,
    ) -> WorkflowRunResult:
        """Execute ACTION/MODEL nodes via registered handlers (no graph-hosted code)."""
        self.assert_permission(principal, WorkflowPermission.RUN)
        order = self.topological_order()
        node_outputs: dict[str, Any] = {}
        results: list[WorkflowNodeResult] = []
        cancelled = False
        failed = False
        seed = dict(inputs or {})

        for node_id in order:
            if policy is not None and request_id is not None and policy.is_cancelled(request_id):
                cancelled = True
                results.append(
                    WorkflowNodeResult(
                        node_id=node_id,
                        status="cancelled",
                        provenance={"reason": "policy_cancel"},
                    )
                )
                for remaining in order[order.index(node_id) + 1 :]:
                    results.append(
                        WorkflowNodeResult(
                            node_id=remaining,
                            status="skipped",
                            provenance={"reason": "upstream_cancel"},
                        )
                    )
                break

            node = self._nodes[node_id]
            inbound = self._gather_inputs(node_id, node_outputs, seed)
            if node.kind in {WorkflowNodeKind.INPUT, WorkflowNodeKind.REFERENCE}:
                value = inbound if inbound else seed.get(node_id, seed)
                node_outputs[node_id] = value
                results.append(
                    WorkflowNodeResult(
                        node_id=node_id,
                        status="ok",
                        output=value,
                        provenance={"kind": node.kind.value},
                    )
                )
                continue
            if node.kind in {
                WorkflowNodeKind.OUTPUT,
                WorkflowNodeKind.ARTIFACT,
                WorkflowNodeKind.DATASET,
                WorkflowNodeKind.REMOTE,
            }:
                node_outputs[node_id] = inbound
                results.append(
                    WorkflowNodeResult(
                        node_id=node_id,
                        status="ok",
                        output=inbound,
                        provenance={"kind": node.kind.value},
                    )
                )
                continue
            if node.kind in {WorkflowNodeKind.ACTION, WorkflowNodeKind.MODEL}:
                action = registry.get_action(node.action_id or "")
                if action is None or action.handler is None:
                    failed = True
                    results.append(
                        WorkflowNodeResult(
                            node_id=node_id,
                            status="failed",
                            error=f"Missing registered handler for action {node.action_id!r}",
                            provenance={"action_id": node.action_id},
                        )
                    )
                    for remaining in order[order.index(node_id) + 1 :]:
                        results.append(
                            WorkflowNodeResult(
                                node_id=remaining,
                                status="skipped",
                                provenance={"reason": "upstream_failure"},
                            )
                        )
                    break
                try:
                    payload = {**dict(node.parameters), **inbound}
                    output = action.handler(**payload) if payload else action.handler()
                    node_outputs[node_id] = output
                    results.append(
                        WorkflowNodeResult(
                            node_id=node_id,
                            status="ok",
                            output=output,
                            provenance={
                                "action_id": node.action_id,
                                "code_version": action.code_version,
                                "model_version": action.model_version,
                            },
                        )
                    )
                except Exception as exc:  # noqa: BLE001
                    failed = True
                    results.append(
                        WorkflowNodeResult(
                            node_id=node_id,
                            status="failed",
                            error=str(exc),
                            provenance={"action_id": node.action_id},
                        )
                    )
                    for remaining in order[order.index(node_id) + 1 :]:
                        results.append(
                            WorkflowNodeResult(
                                node_id=remaining,
                                status="skipped",
                                provenance={"reason": "upstream_failure"},
                            )
                        )
                    break

        terminal = {
            nid: node_outputs[nid]
            for nid, n in self._nodes.items()
            if n.kind == WorkflowNodeKind.OUTPUT and nid in node_outputs
        }
        if cancelled:
            status = "cancelled"
        elif failed:
            status = "partial" if any(r.status == "ok" for r in results) else "failed"
        else:
            status = "completed"
        return WorkflowRunResult(
            workflow_id=self.workflow_id,
            status=status,
            nodes=tuple(results),
            outputs=terminal,
            request_id=request_id,
        )

    def migrate_schema(self, target_version: str) -> None:
        # Identity migration for v1; future versions append transforms here.
        if self.schema_version == target_version:
            return
        allowed = {"1"}
        if target_version not in allowed:
            raise WorkflowError(
                f"Unsupported schema migration to {target_version}",
                code=HED_WORKFLOW_0001,
            )
        if self.schema_version not in allowed:
            raise WorkflowError(
                f"Unsupported schema migration from {self.schema_version}",
                code=HED_WORKFLOW_0001,
            )
        raise WorkflowError(
            f"No migration transform from {self.schema_version} to {target_version}",
            code=HED_WORKFLOW_0001,
        )

    def _port(self, node_id: str, port_id: str, direction: str) -> WorkflowPort:
        node = self._nodes[node_id]
        for port in node.ports:
            if port.port_id == port_id and port.direction == direction:
                return port
        raise WorkflowError(
            f"Missing {direction} port {port_id!r} on {node_id!r}",
            code=HED_WORKFLOW_0001,
        )

    def _validate_node(self, node: WorkflowNode, *, existing: set[str] | None = None) -> None:
        self._reject_forbidden_parameters(node.parameters)
        known = set(self._nodes) if existing is None else (set(self._nodes) | existing)
        if node.node_id in known:
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

    def _insert_node(self, node: WorkflowNode) -> None:
        self._validate_node(node)
        self._nodes[node.node_id] = node

    def _gather_inputs(
        self,
        node_id: str,
        node_outputs: Mapping[str, Any],
        seed: Mapping[str, Any],
    ) -> dict[str, Any]:
        inbound: dict[str, Any] = {}
        for frm, fp, to, tp in self._edges:
            if to != node_id:
                continue
            upstream = node_outputs.get(frm, seed.get(frm))
            if isinstance(upstream, Mapping) and fp in upstream:
                inbound[tp] = upstream[fp]
            else:
                inbound[tp] = upstream
        return inbound

    def _reject_forbidden_parameters(self, parameters: Mapping[str, JsonValue]) -> None:
        for key in parameters:
            lowered = key.lower()
            if lowered in FORBIDDEN_PARAM_KEYS or any(
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
