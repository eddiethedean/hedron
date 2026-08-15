"""Registered demo actions and callable adapters."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from hedron_core.diagnostics import HedronError


class ModelDemoError(ValueError):
    """Fail-closed model-demo generation or feedback policy error."""

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


@dataclass(frozen=True, slots=True)
class RegisteredAction:
    """Explicitly registered typed action available for demo composition."""

    action_id: str
    input_schema: Mapping[str, Any]
    output_schema: Mapping[str, Any]
    side_effects: tuple[str, ...] = ()
    authorization_required: bool = True
    resource_policy: str | None = None
    http_exposed: bool = False
    mcp_exposed: bool = False
    description: str = ""
    preprocessing_version: str = "1"
    code_version: str = "1"
    model_version: str = "1"
    handler: Callable[..., Any] | None = None


@dataclass(frozen=True, slots=True)
class RegisteredCallableAdapter:
    """Callable adapter with explicit schemas and policies (never auto-published)."""

    adapter_id: str
    callable_ref: Callable[..., Any]
    input_schema: Mapping[str, Any]
    output_schema: Mapping[str, Any]
    side_effects: tuple[str, ...] = ()
    authorization_required: bool = True
    resource_policy: str | None = None
    http_exposed: bool = False
    mcp_exposed: bool = False
    description: str = ""
    preprocessing_version: str = "1"
    code_version: str = "1"
    model_version: str = "1"


@dataclass
class ActionRegistry:
    """Explicit registry — demos fail closed without a matching entry."""

    _actions: dict[str, RegisteredAction] = field(default_factory=dict)
    _adapters: dict[str, RegisteredCallableAdapter] = field(default_factory=dict)

    def register_action(self, action: RegisteredAction) -> None:
        if action.action_id in self._actions:
            raise ModelDemoError(f"Action already registered: {action.action_id!r}")
        self._actions[action.action_id] = action

    def register_adapter(self, adapter: RegisteredCallableAdapter) -> None:
        if adapter.adapter_id in self._adapters:
            raise ModelDemoError(f"Adapter already registered: {adapter.adapter_id!r}")
        self._adapters[adapter.adapter_id] = adapter

    def get_action(self, action_id: str) -> RegisteredAction | None:
        return self._actions.get(action_id)

    def get_adapter(self, adapter_id: str) -> RegisteredCallableAdapter | None:
        return self._adapters.get(adapter_id)
