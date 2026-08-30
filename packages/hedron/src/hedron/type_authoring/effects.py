"""Declared-effect checking at response conversion (does not execute)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import cast

from hedron.type_authoring.normalize import CompiledTypeHandler
from hedron_core.codes import HED_TYPE_0006
from hedron_core.diagnostics import error
from hedron_core.updates import Patch, PatchSet, RefreshIntent

__all__ = ["assert_declared_effects", "logical_ids_from_result"]


def logical_ids_from_result(result: object) -> tuple[str, ...]:
    ids: list[str] = []
    if isinstance(result, RefreshIntent):
        for target in result.targets:
            logical = getattr(target, "logical_id", None)
            if isinstance(logical, str):
                ids.append(logical)
    elif isinstance(result, PatchSet):
        for item in (result.primary, *result.secondary):
            logical = getattr(item.target, "logical_id", None)
            if isinstance(logical, str):
                ids.append(logical)
    elif isinstance(result, Patch):
        logical = getattr(result.target, "logical_id", None)
        if isinstance(logical, str):
            ids.append(logical)
    return tuple(ids)


def assert_declared_effects(
    compiled: CompiledTypeHandler | None,
    result: object,
    *,
    app_id: str,
) -> None:
    if compiled is None:
        return
    declared = set(compiled.declared_refresh_ids) | set(compiled.declared_update_ids)
    if not declared:
        return
    actual = logical_ids_from_result(result)
    if isinstance(result, RefreshIntent) and compiled.declared_refresh_ids:
        allowed: Sequence[str] = compiled.declared_refresh_ids
    elif isinstance(result, (Patch, PatchSet)) and compiled.declared_update_ids:
        allowed = compiled.declared_update_ids
    elif not actual:
        return
    else:
        allowed = tuple(declared)
    extra = [item for item in actual if item not in set(allowed)]
    if extra:
        raise error(
            HED_TYPE_0006,
            title="Undeclared command effect",
            explanation=f"Result targets {extra} are not in the declared set {list(allowed)}.",
            remediation=(
                "Add the handles to Refreshes(...)/Updates(...) or return a declared subset."
            ),
        )
    for target in _targets(cast(object, result)):
        owner = str(getattr(target, "app_id", "") or "")
        if owner and owner != app_id:
            raise error(
                HED_TYPE_0006,
                title="Cross-app effect is not allowed",
                explanation=f"Target {getattr(target, 'logical_id', '')!r} belongs to another app.",
                remediation="Declare and emit only same-app handles.",
            )


def _targets(result: object) -> tuple[object, ...]:
    if isinstance(result, RefreshIntent):
        return tuple(result.targets)
    if isinstance(result, PatchSet):
        return (result.primary.target, *(item.target for item in result.secondary))
    if isinstance(result, Patch):
        return (result.target,)
    return ()
