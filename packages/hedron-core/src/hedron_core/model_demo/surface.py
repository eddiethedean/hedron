"""InferenceInterface / ModelDemo surface composition."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from hedron_core.codes import HED_DEMO_0001, HED_DEMO_0002, HED_DEMO_0003
from hedron_core.diagnostics import error
from hedron_core.model_demo.actions import (
    ActionRegistry,
    ModelDemoError,
)


@dataclass(frozen=True, slots=True)
class InferenceInterface:
    """Reviewable input/result surface derived from a registered action or adapter."""

    interface_id: str
    source_id: str
    source_kind: str  # "action" | "adapter"
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    description: str = ""
    live_mode: bool = False
    debounce_ms: int = 0
    allow_submit: bool = True
    allow_clear: bool = True
    allow_stop: bool = True
    component_overrides: Mapping[str, str] = field(default_factory=dict[str, str])
    input_schema: Mapping[str, Any] = field(default_factory=dict[str, Any])
    output_schema: Mapping[str, Any] = field(default_factory=dict[str, Any])
    http_exposed: bool = False
    mcp_exposed: bool = False
    resource_policy: str | None = None
    authorization_required: bool = True


@dataclass
class ModelDemo:
    """Composition layer that builds ``InferenceInterface`` only from the registry."""

    registry: ActionRegistry
    title: str = "Model demo"
    _interfaces: dict[str, InferenceInterface] = field(
        default_factory=dict[str, InferenceInterface], init=False
    )

    def build_from_action(
        self,
        action_id: str,
        *,
        interface_id: str | None = None,
        inputs: Sequence[str] | None = None,
        outputs: Sequence[str] | None = None,
        live_mode: bool = False,
        debounce_ms: int = 0,
        component_overrides: Mapping[str, str] | None = None,
    ) -> InferenceInterface:
        action = self.registry.get_action(action_id)
        if action is None:
            raise ModelDemoError(
                f"Unregistered action: {action_id!r}",
                code=HED_DEMO_0001,
                diagnostic=error(
                    HED_DEMO_0001,
                    title="Unregistered action",
                    explanation="InferenceInterface requires an explicitly registered action.",
                    remediation="Register the action before building a demo.",
                ),
            )
        return self._build(
            source_id=action.action_id,
            source_kind="action",
            interface_id=interface_id or f"demo-{action.action_id}",
            input_schema=action.input_schema,
            output_schema=action.output_schema,
            side_effects=action.side_effects,
            authorization_required=action.authorization_required,
            resource_policy=action.resource_policy,
            http_exposed=action.http_exposed,
            mcp_exposed=action.mcp_exposed,
            description=action.description,
            inputs=inputs,
            outputs=outputs,
            live_mode=live_mode,
            debounce_ms=debounce_ms,
            component_overrides=component_overrides,
        )

    def build_from_adapter(
        self,
        adapter_id: str,
        *,
        interface_id: str | None = None,
        inputs: Sequence[str] | None = None,
        outputs: Sequence[str] | None = None,
        live_mode: bool = False,
        debounce_ms: int = 0,
        component_overrides: Mapping[str, str] | None = None,
    ) -> InferenceInterface:
        adapter = self.registry.get_adapter(adapter_id)
        if adapter is None:
            raise ModelDemoError(
                f"Unregistered callable adapter: {adapter_id!r}",
                code=HED_DEMO_0001,
                diagnostic=error(
                    HED_DEMO_0001,
                    title="Unregistered callable",
                    explanation="Arbitrary callables cannot become demos without registration.",
                    remediation="Register a RegisteredCallableAdapter with explicit policies.",
                ),
            )
        return self._build(
            source_id=adapter.adapter_id,
            source_kind="adapter",
            interface_id=interface_id or f"demo-{adapter.adapter_id}",
            input_schema=adapter.input_schema,
            output_schema=adapter.output_schema,
            side_effects=adapter.side_effects,
            authorization_required=adapter.authorization_required,
            resource_policy=adapter.resource_policy,
            http_exposed=adapter.http_exposed,
            mcp_exposed=adapter.mcp_exposed,
            description=adapter.description,
            inputs=inputs,
            outputs=outputs,
            live_mode=live_mode,
            debounce_ms=debounce_ms,
            component_overrides=component_overrides,
        )

    def build_from_callable(self, fn: Callable[..., Any], **_: Any) -> InferenceInterface:
        """Fail closed — bare callables are never auto-published."""
        raise ModelDemoError(
            "Cannot build InferenceInterface from an unregistered callable",
            code=HED_DEMO_0001,
            diagnostic=error(
                HED_DEMO_0001,
                title="Unregistered callable",
                explanation="Passing a raw callable is rejected.",
                remediation="Use register_adapter with explicit schemas and policies.",
            ),
        )

    def get(self, interface_id: str) -> InferenceInterface | None:
        return self._interfaces.get(interface_id)

    def _build(
        self,
        *,
        source_id: str,
        source_kind: str,
        interface_id: str,
        input_schema: Mapping[str, Any],
        output_schema: Mapping[str, Any],
        side_effects: tuple[str, ...],
        authorization_required: bool,
        resource_policy: str | None,
        http_exposed: bool,
        mcp_exposed: bool,
        description: str,
        inputs: Sequence[str] | None,
        outputs: Sequence[str] | None,
        live_mode: bool,
        debounce_ms: int,
        component_overrides: Mapping[str, str] | None,
    ) -> InferenceInterface:
        if not input_schema or not output_schema:
            raise ModelDemoError(
                "Ambiguous or missing input/output schema",
                code=HED_DEMO_0002,
                diagnostic=error(
                    HED_DEMO_0002,
                    title="Ambiguous schema",
                    explanation="Both input_schema and output_schema must be non-empty.",
                    remediation="Declare typed schemas on the registered action/adapter.",
                ),
            )
        undeclared = [s for s in side_effects if not s.strip()]
        if undeclared or (side_effects and any(s == "undeclared" for s in side_effects)):
            raise ModelDemoError(
                "Undeclared side effects",
                code=HED_DEMO_0002,
                diagnostic=error(
                    HED_DEMO_0002,
                    title="Undeclared side effects",
                    explanation="Side effects must be named explicitly.",
                    remediation="List concrete side-effect identifiers or use an empty tuple.",
                ),
            )
        if authorization_required and not resource_policy:
            raise ModelDemoError(
                "Missing resource policy for authorized demo",
                code=HED_DEMO_0003,
                diagnostic=error(
                    HED_DEMO_0003,
                    title="Missing resource policy",
                    explanation="Authorized demos require an explicit resource_policy.",
                    remediation="Set resource_policy on the registered action/adapter.",
                ),
            )
        if live_mode and not resource_policy:
            raise ModelDemoError(
                "Live/debounced mode requires resource policy",
                code=HED_DEMO_0003,
                diagnostic=error(
                    HED_DEMO_0003,
                    title="Missing live resource policy",
                    explanation="Declared live mode needs rate/resource policy.",
                    remediation="Provide resource_policy before enabling live_mode.",
                ),
            )
        # Accidental exposure: MCP/HTTP flags are independent; both default false.
        # Building a demo never flips them on.
        resolved_inputs = tuple(inputs) if inputs is not None else tuple(input_schema.keys())
        resolved_outputs = tuple(outputs) if outputs is not None else tuple(output_schema.keys())
        iface = InferenceInterface(
            interface_id=interface_id,
            source_id=source_id,
            source_kind=source_kind,
            inputs=resolved_inputs,
            outputs=resolved_outputs,
            description=description,
            live_mode=live_mode,
            debounce_ms=debounce_ms,
            component_overrides=dict(component_overrides or {}),
            input_schema=dict(input_schema),
            output_schema=dict(output_schema),
            http_exposed=http_exposed,
            mcp_exposed=mcp_exposed,
            resource_policy=resource_policy,
            authorization_required=authorization_required,
        )
        self._interfaces[interface_id] = iface
        return iface
