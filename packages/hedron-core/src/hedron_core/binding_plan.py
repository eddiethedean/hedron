"""Boundary binding strategy record. BindingPlan stays the 0.43 URL plan."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Literal

from hedron_core.codes import HED_FP_0002
from hedron_core.diagnostics import error
from hedron_core.type_schema import payload_fingerprint
from hedron_core.typing_aliases import JsonObject, JsonValue
from hedron_core.updates import BindingPlan

__all__ = [
    "BindingStrategy",
    "BoundaryBindingPlan",
    "NATIVE_MODEL_ELIGIBLE_LOCATIONS",
    "compile_boundary_binding",
]

BindingStrategy = Literal["native-model", "expanded-fields"]
NATIVE_MODEL_ELIGIBLE_LOCATIONS = frozenset({"query", "header", "cookie", "form"})
SequenceStr = Sequence[str]


@dataclass(frozen=True, slots=True)
class BoundaryBindingPlan:
    """Strategy record beside BindingPlan. Does not replace path/query identity."""

    source: str = ""
    model_identity: str = ""
    strategy: BindingStrategy = "expanded-fields"
    field_locations: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    extra_field_policy: str = "forbid"
    content_type: str = ""
    adapter_disposition: str = "fastapi"
    fallback_reason: str = ""
    structural: BindingPlan = field(default_factory=BindingPlan)
    force_expanded: bool = False

    def fingerprint(self) -> str:
        payload: JsonObject = {
            "source": self.source,
            "model_identity": self.model_identity,
            "strategy": self.strategy,
            "field_locations": list(self.field_locations),
            "aliases": list(self.aliases),
            "extra_field_policy": self.extra_field_policy,
            "content_type": self.content_type,
            "adapter_disposition": self.adapter_disposition,
            "fallback_reason": self.fallback_reason,
            "force_expanded": self.force_expanded,
            "path_params": list(self.structural.path_params),
            "query_params": list(self.structural.query_params),
        }
        return payload_fingerprint(payload)


def compile_boundary_binding(
    *,
    source: str,
    model_identity: str,
    locations: SequenceStr,
    aliases: SequenceStr = (),
    structural: BindingPlan | None = None,
    has_files: bool = False,
    portable_adapter: bool = False,
    force_expanded: bool = False,
    incompatible_aliases: bool = False,
    flask_django: bool = False,
    extra_field_policy: str = "forbid",
    content_type: str = "",
) -> BoundaryBindingPlan:
    """Choose native-model only when FastAPI native Pydantic models are equivalent."""
    locs = tuple(locations)
    unique = {item for item in locs if item}
    structural_plan = structural or BindingPlan()
    fallback = ""
    strategy: BindingStrategy = "native-model"
    if force_expanded:
        strategy, fallback = "expanded-fields", "author-override"
    elif flask_django or portable_adapter:
        strategy, fallback = "expanded-fields", "portable-adapter"
    elif has_files:
        strategy, fallback = "expanded-fields", "multipart-file"
    elif incompatible_aliases:
        strategy, fallback = "expanded-fields", "incompatible-aliases"
    elif "path" in unique:
        strategy, fallback = "expanded-fields", "mixed-path-query"
    elif not unique:
        strategy, fallback = "expanded-fields", "unmodeled"
    elif unique == {"form"}:
        # FastAPI Form() on a Pydantic model is not equivalent to expanded Form
        # fields: urlencoded POSTs bind as a JSON body (model_attributes_type).
        strategy, fallback = "expanded-fields", "form-not-equivalent"
    elif unique - NATIVE_MODEL_ELIGIBLE_LOCATIONS:
        strategy, fallback = "expanded-fields", "ineligible-location"
    elif len(unique) != 1:
        strategy, fallback = "expanded-fields", "mixed-locations"
    if strategy == "native-model" and unique == {"form"} and not content_type:
        content_type = "application/x-www-form-urlencoded"
    if strategy == "native-model" and not unique:
        raise error(
            HED_FP_0002,
            title="Native-model selected without field locations",
            explanation="Equivalence requires a single eligible location.",
            remediation="Keep expanded-fields via apply_modeled_signature.",
        )
    return BoundaryBindingPlan(
        source=source,
        model_identity=model_identity,
        strategy=strategy,
        field_locations=locs,
        aliases=tuple(aliases),
        extra_field_policy=extra_field_policy,
        content_type=content_type,
        adapter_disposition="projection_adapter" if flask_django else "fastapi",
        fallback_reason=fallback,
        structural=structural_plan,
        force_expanded=force_expanded,
    )


def as_mapping(plan: BoundaryBindingPlan) -> Mapping[str, JsonValue]:
    return {
        "strategy": plan.strategy,
        "fallback_reason": plan.fallback_reason,
        "model_identity": plan.model_identity,
        "fingerprint": plan.fingerprint(),
    }
