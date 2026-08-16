"""Pydantic BindingAdapter implementing the 0.43 binding seam."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace

from pydantic import BaseModel, ValidationError

from hedron_core.codes import HED_TYPE_0001, HED_TYPE_0003, HED_TYPE_0010
from hedron_core.diagnostics import error
from hedron_core.identifiers import instance_id
from hedron_core.updates import (
    IDENTITY_ALGO_VERSION,
    BindingPlan,
    BoundValues,
    structural_bind,
)

__all__ = ["PydanticBindingAdapter"]


def _values_for_model(
    model_type: type[BaseModel], values: Mapping[str, object]
) -> dict[str, object]:
    """Map Python field names to Pydantic aliases so validation keys stay consistent."""
    name_to_key = {name: (info.alias or name) for name, info in model_type.model_fields.items()}
    out: dict[str, object] = {}
    for key, value in values.items():
        out[name_to_key.get(key, key)] = value
    return out


def _plan_values(
    model_type: type[BaseModel], dumped: Mapping[str, object], plan: BindingPlan
) -> dict[str, object]:
    """Select dumped field values using BindingPlan keys (path placeholders / aliases)."""
    alias_to_name = {
        info.alias: name for name, info in model_type.model_fields.items() if info.alias
    }
    out: dict[str, object] = {}
    for key in (*plan.path_params, *plan.query_params):
        if key in dumped:
            out[key] = dumped[key]
            continue
        python_name = alias_to_name.get(key)
        if python_name is not None and python_name in dumped:
            out[key] = dumped[python_name]
    return out


_BLOCKED_BIND_NAMES = frozenset(
    {
        "request",
        "websocket",
        "actor",
        "principal",
        "user",
        "current_user",
        "auth",
        "session",
        "state",
        "app",
    }
)


class PydanticBindingAdapter:
    """Compiled Pydantic validator used for bind, reconstruction, form, and scenarios."""

    def __init__(
        self,
        model_type: type[BaseModel],
        *,
        injected_names: frozenset[str] = frozenset(),
        identity_fields: tuple[str, ...] = (),
        sensitive_fields: tuple[str, ...] = (),
    ) -> None:
        self.model_type = model_type
        self.injected_names = frozenset(injected_names) | _BLOCKED_BIND_NAMES
        self.identity_fields = identity_fields
        self.sensitive_fields = sensitive_fields

    def validate(self, values: Mapping[str, object] | BaseModel) -> BaseModel:
        if isinstance(values, self.model_type):
            return values
        if isinstance(values, BaseModel):
            raise error(
                HED_TYPE_0003,
                title="Cross-model bind instance",
                explanation=f"Expected {self.model_type.__name__}, got {type(values).__name__}.",
                remediation="Pass the registered ViewParams/FormBody model or matching fields.",
            )
        self._reject_injected(values)
        try:
            return self.model_type.model_validate(_values_for_model(self.model_type, values))
        except ValidationError as exc:
            errors = exc.errors()[:100]
            paths = [".".join(str(part) for part in item.get("loc", ())) for item in errors]
            raise error(
                HED_TYPE_0003,
                title="Boundary model validation failed",
                explanation=f"Invalid fields: {paths}",
                remediation="Correct the bind/form values against the Pydantic model.",
            ) from exc

    def dump(self, model: BaseModel) -> dict[str, object]:
        return dict(model.model_dump(mode="python"))

    def bind(self, plan: BindingPlan, values: Mapping[str, object], *, path: str) -> BoundValues:
        model = self.validate(values)
        dumped = self.dump(model)
        plan_keys = set(plan.path_params) | set(plan.query_params)
        public_name = {
            name: (info.alias or name) for name, info in self.model_type.model_fields.items()
        }
        for name in self.sensitive_fields:
            exposed = name in plan_keys or public_name.get(name, name) in plan_keys
            if name in dumped and exposed:
                raise error(
                    HED_TYPE_0010,
                    title="Sensitive value cannot enter a public URL",
                    explanation=f"Field {name!r} is Sensitive and cannot be path/query-bound.",
                    remediation="Keep secrets on dependencies; use a non-secret public key.",
                )
        filtered = _plan_values(self.model_type, dumped, plan)
        bound = structural_bind(plan, filtered, path=path)
        if self.identity_fields:
            identity = {name: dumped[name] for name in self.identity_fields if name in dumped}
            overlap = set(identity) & set(self.sensitive_fields)
            if overlap:
                raise error(
                    HED_TYPE_0010,
                    title="Sensitive field cannot be an InstanceKey",
                    explanation=f"Fields {sorted(overlap)} cannot drive identity.",
                    remediation="Remove Sensitive or InstanceKey from the conflicting field.",
                )
            token = instance_id({"v": IDENTITY_ALGO_VERSION, "identity": identity})[2:]
            return replace(bound, instance_token=token)
        return bound

    def _reject_injected(self, values: Mapping[str, object]) -> None:
        blocked = sorted(set(values) & self.injected_names)
        if blocked:
            raise error(
                HED_TYPE_0001,
                title="Bind source is not a boundary field",
                explanation=(
                    f"Names {blocked} belong to dependencies, request, or security context."
                ),
                remediation="Pass only ViewParams/FormBody fields to bind() and form input.",
            )
