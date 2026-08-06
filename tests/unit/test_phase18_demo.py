"""Phase 0.18 DEMO-018: InferenceInterface / ModelDemo fail-closed generation."""

from __future__ import annotations

import pytest

from hedron_core import (
    ActionRegistry,
    ModelDemo,
    ModelDemoError,
    RegisteredAction,
    RegisteredCallableAdapter,
)
from hedron_core.codes import HED_DEMO_0001, HED_DEMO_0002, HED_DEMO_0003


def _action(**overrides: object) -> RegisteredAction:
    base = dict(
        action_id="classify",
        input_schema={"text": "string"},
        output_schema={"label": "string"},
        side_effects=(),
        authorization_required=True,
        resource_policy="gpu-small",
        http_exposed=False,
        mcp_exposed=False,
        description="Classify text",
    )
    base.update(overrides)
    return RegisteredAction(**base)  # type: ignore[arg-type]


def test_build_from_registered_action() -> None:
    registry = ActionRegistry()
    registry.register_action(_action())
    demo = ModelDemo(registry=registry)
    iface = demo.build_from_action("classify", live_mode=False)
    assert iface.source_id == "classify"
    assert iface.inputs == ("text",)
    assert iface.http_exposed is False
    assert iface.mcp_exposed is False


def test_unregistered_callable_fails() -> None:
    demo = ModelDemo(registry=ActionRegistry())

    def raw(x: str) -> str:
        return x

    with pytest.raises(ModelDemoError) as exc:
        demo.build_from_callable(raw)
    assert exc.value.code == HED_DEMO_0001

    with pytest.raises(ModelDemoError) as exc2:
        demo.build_from_action("missing")
    assert exc2.value.code == HED_DEMO_0001


def test_ambiguous_schema_and_missing_policy() -> None:
    registry = ActionRegistry()
    registry.register_action(
        _action(input_schema={}, output_schema={"y": "string"}, resource_policy="g")
    )
    demo = ModelDemo(registry=registry)
    with pytest.raises(ModelDemoError) as exc:
        demo.build_from_action("classify")
    assert exc.value.code == HED_DEMO_0002

    registry2 = ActionRegistry()
    registry2.register_action(_action(resource_policy=None))
    demo2 = ModelDemo(registry=registry2)
    with pytest.raises(ModelDemoError) as exc2:
        demo2.build_from_action("classify")
    assert exc2.value.code == HED_DEMO_0003


def test_adapter_registration_and_no_accidental_exposure() -> None:
    def fn(text: str) -> dict[str, str]:
        return {"label": text}

    registry = ActionRegistry()
    registry.register_adapter(
        RegisteredCallableAdapter(
            adapter_id="adapt",
            callable_ref=fn,
            input_schema={"text": "string"},
            output_schema={"label": "string"},
            resource_policy="cpu",
            http_exposed=False,
            mcp_exposed=False,
        )
    )
    iface = ModelDemo(registry=registry).build_from_adapter("adapt")
    assert iface.source_kind == "adapter"
    assert iface.http_exposed is False
