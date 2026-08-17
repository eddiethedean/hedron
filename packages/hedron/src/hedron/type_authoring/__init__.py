"""Type-driven authoring public API (phase 0.44)."""

from __future__ import annotations

from hedron.type_authoring.adapter import PydanticBindingAdapter
from hedron.type_authoring.classes import (
    CommandHandler,
    RefreshableView,
    class_config_conflict,
    compile_command_class,
    compile_view_class,
)
from hedron.type_authoring.depends import DependsOn
from hedron.type_authoring.effects import assert_declared_effects
from hedron.type_authoring.forms import generate_form
from hedron.type_authoring.markers import Control, FormBody, Refreshes, Updates, ViewParams
from hedron.type_authoring.normalize import CompiledTypeHandler, TypeNormalizer, inspect_handler
from hedron.type_authoring.outcomes import CommandResult, OutcomeMap, case
from hedron.type_authoring.signature import apply_modeled_signature, reconstruct_kwargs

__all__ = [
    "CommandHandler",
    "CommandResult",
    "CompiledTypeHandler",
    "Control",
    "DependsOn",
    "FormBody",
    "OutcomeMap",
    "PydanticBindingAdapter",
    "RefreshableView",
    "Refreshes",
    "TypeNormalizer",
    "Updates",
    "ViewParams",
    "assert_declared_effects",
    "apply_modeled_signature",
    "case",
    "class_config_conflict",
    "compile_command_class",
    "compile_view_class",
    "generate_form",
    "inspect_handler",
    "reconstruct_kwargs",
]
