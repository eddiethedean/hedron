"""Closed OutcomeMap builder (D-076 spelling: OutcomeMap(case(...), ...))."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Annotated, Any, Generic, TypeVar, get_args, get_origin

from pydantic import BaseModel

from hedron.type_authoring.markers import Refreshes, Updates
from hedron_core.codes import HED_TYPE_0007
from hedron_core.diagnostics import error

ResultT = TypeVar("ResultT")

__all__ = ["CommandResult", "OutcomeCase", "OutcomeMap", "case"]

CommandResult = object


@dataclass(frozen=True, slots=True)
class OutcomeCase:
    variant: type[Any]
    render: Callable[..., Any]
    status: int = 200
    effects: Refreshes | Updates | None = None
    fallback: str | None = None


def case(
    variant: type[Any],
    *,
    render: Callable[..., Any],
    status: int = 200,
    effects: Refreshes | Updates | None = None,
    fallback: str | None = None,
) -> OutcomeCase:
    if not isinstance(status, int) or status < 100 or status > 599:
        raise error(
            HED_TYPE_0007,
            title="Invalid outcome status",
            explanation=f"status={status} is not a valid HTTP status.",
            remediation="Pass a documented response status.",
        )
    return OutcomeCase(
        variant=variant,
        render=render,
        status=status,
        effects=effects,
        fallback=fallback,
    )


class OutcomeMap(Generic[ResultT]):
    """Complete, non-overlapping discriminator coverage for a command result union."""

    def __init__(self, *cases: OutcomeCase) -> None:
        if not cases:
            raise error(
                HED_TYPE_0007,
                title="Empty OutcomeMap",
                explanation="OutcomeMap requires at least one case(...).",
                remediation="Map every discriminator variant explicitly.",
            )
        seen: dict[type[Any], OutcomeCase] = {}
        for item in cases:
            if not isinstance(item, OutcomeCase):
                raise error(
                    HED_TYPE_0007,
                    title="Invalid OutcomeMap entry",
                    explanation="OutcomeMap only accepts case(...) entries.",
                    remediation="Use OutcomeMap(case(Variant, render=...), ...).",
                )
            if item.variant in seen:
                raise error(
                    HED_TYPE_0007,
                    title="Overlapping OutcomeMap variant",
                    explanation=f"{item.variant!r} is mapped more than once.",
                    remediation="Give each discriminator variant exactly one case.",
                )
            seen[item.variant] = item
        self._cases = tuple(cases)

    @property
    def cases(self) -> tuple[OutcomeCase, ...]:
        return self._cases

    @property
    def variant_ids(self) -> tuple[str, ...]:
        return tuple(getattr(item.variant, "__name__", str(item.variant)) for item in self._cases)

    def validate_union(self, annotation: object) -> None:
        variants = _union_variants(annotation)
        if not variants:
            return
        mapped = {item.variant for item in self._cases}
        missing = [item for item in variants if item not in mapped]
        extra = [item.variant for item in self._cases if item.variant not in variants]
        if missing or extra:
            raise error(
                HED_TYPE_0007,
                title="Incomplete OutcomeMap coverage",
                explanation=f"missing={_names(missing)} extra={_names(extra)}",
                remediation="Cover every discriminator variant exactly once.",
            )

    def map_result(self, value: object) -> tuple[object, int, Refreshes | Updates | None]:
        if isinstance(value, BaseModel) and not any(
            isinstance(value, item.variant) for item in self._cases
        ):
            raise error(
                HED_TYPE_0007,
                title="Unmapped command result model",
                explanation="Arbitrary BaseModel returns are not auto-rendered.",
                remediation="Return a mapped OutcomeMap variant or a Node/Interaction value.",
            )
        for item in self._cases:
            if isinstance(value, item.variant):
                return item.render(value), item.status, item.effects
        return value, 200, None


def _names(types: Sequence[type[Any]]) -> list[str]:
    return [getattr(item, "__name__", str(item)) for item in types]


def _union_variants(annotation: object) -> tuple[type[Any], ...]:
    if annotation is inspect.Parameter.empty:
        return ()
    origin = get_origin(annotation)
    if origin is Annotated:
        args = get_args(annotation)
        return _union_variants(args[0]) if args else ()
    alias_value = getattr(annotation, "__value__", None)
    if type(annotation).__name__ == "TypeAliasType" and alias_value is not None:
        return _union_variants(alias_value)
    args = get_args(annotation)
    if origin is None and not args:
        if isinstance(annotation, type):
            return (annotation,)
        name = type(annotation).__name__
        if name in {"UnionType", "Union"}:
            args = getattr(annotation, "__args__", ())
        else:
            return ()
    variants: list[type[Any]] = []
    for arg in args:
        if arg is type(None):
            continue
        nested = _union_variants(arg)
        if nested:
            variants.extend(nested)
        elif isinstance(arg, type):
            variants.append(arg)
    return tuple(variants)
