"""Workflow graph types."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from hedron_core.compat import StrEnum
from hedron_core.diagnostics import HedronError
from hedron_core.typing_aliases import JsonValue


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
    parameters: Mapping[str, JsonValue] = field(default_factory=dict[str, JsonValue])
    secret_refs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PublishedRevision:
    revision_id: str
    version: int
    published_at: float
    publisher: str
    immutable: bool = True
    snapshot: Mapping[str, Any] = field(default_factory=dict[str, Any])


@dataclass(frozen=True, slots=True)
class WorkflowEditorView:
    """Non-spatial structured editor: list / outline / table rows."""

    mode: str  # "list" | "outline" | "table"
    rows: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True, slots=True)
class WorkflowNodeResult:
    """Per-node execution outcome with provenance (no host code from graph JSON)."""

    node_id: str
    status: str  # "ok" | "skipped" | "failed" | "cancelled"
    output: Any = None
    error: str | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict[str, Any])


@dataclass(frozen=True, slots=True)
class WorkflowRunResult:
    """Aggregate workflow run with partial-failure semantics."""

    workflow_id: str
    status: str  # "completed" | "partial" | "cancelled" | "failed"
    nodes: tuple[WorkflowNodeResult, ...]
    outputs: Mapping[str, Any] = field(default_factory=dict[str, Any])
    request_id: str | None = None


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
FORBIDDEN_PARAM_KEYS = _FORBIDDEN_PARAM_KEYS
