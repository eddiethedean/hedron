"""Jinja TypeSchema disposition: registered schema only; no annotation evaluation."""

from __future__ import annotations

from hedron_core.codes import HED_TYPE_0009
from hedron_core.diagnostics import error
from hedron_core.type_schema import type_schema_from_descriptor
from hedron_core.typing_aliases import JsonObject
from hedron_core.updates import BaseHandleDescriptor
from hedron_jinja.handles import resolve_registered_handle

__all__ = ["refuse_annotation_evaluation", "registered_type_schema"]


def refuse_annotation_evaluation(*, detail: str = "template annotation") -> None:
    """Templates must not evaluate type annotations."""
    raise error(
        HED_TYPE_0009,
        title="Jinja must not evaluate type annotations",
        explanation=f"{detail} evaluation is refused on the Jinja adapter.",
        remediation="Pass a registered handle logical id and read TypeSchema from the descriptor.",
    )


def registered_type_schema(
    logical_id: str,
    *,
    app_id: str | None = None,
) -> JsonObject | None:
    descriptor: BaseHandleDescriptor = resolve_registered_handle(logical_id, app_id=app_id)
    schema = type_schema_from_descriptor(descriptor)
    if schema is None:
        return None
    return schema.as_mapping()
