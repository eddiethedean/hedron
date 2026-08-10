"""Hedron model bases backed by constrained Pydantic."""

from __future__ import annotations

import re
import types
from collections.abc import Callable, Mapping, Sized
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated, Any, ClassVar, Literal, Union, get_args, get_origin

from pydantic import BaseModel, ConfigDict, model_serializer, model_validator
from pydantic.fields import FieldInfo

from hedron_core.diagnostics import HedronError, error
from hedron_core.field import hedron_meta
from hedron_core.security import SafeUrl, Secret, TrustedHtml, redact_value

_PRIMITIVES = {str, int, float, bool, bytes, Decimal, date, datetime, type(None)}


def _is_supported_annotation(annotation: Any, *, depth: int = 0) -> bool:
    if depth > 8:
        return False
    if isinstance(annotation, str):
        return True
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is None:
        if annotation in _PRIMITIVES:
            return True
        if isinstance(annotation, type):
            try:
                if issubclass(annotation, Enum):
                    return True
                if issubclass(annotation, (Model, SafeUrl, TrustedHtml)):
                    return True
                if issubclass(annotation, Secret):
                    return True
            except TypeError:
                return False
            return False
        return False

    if origin in {Union, types.UnionType}:
        return all(_is_supported_annotation(a, depth=depth + 1) for a in args)
    if origin in {list, set, frozenset, tuple}:
        if not args:
            return False
        return all(a is Ellipsis or _is_supported_annotation(a, depth=depth + 1) for a in args)
    if origin in {dict, Mapping}:
        if len(args) != 2:
            return False
        return args[0] is str and _is_supported_annotation(args[1], depth=depth + 1)
    if origin is Secret:
        return len(args) == 0 or _is_supported_annotation(args[0], depth=depth + 1)
    if origin is Literal:
        return True
    if origin is Annotated:
        return _is_supported_annotation(args[0], depth=depth + 1) if args else False
    if origin is Callable:
        return False
    return False


def _unwrap_for_constraints(value: Any) -> Any:
    if isinstance(value, Secret):
        return value.reveal()
    return value


def _apply_hedron_constraints(field_name: str, value: Any, meta: Mapping[str, object]) -> None:
    if value is None:
        return
    inner = _unwrap_for_constraints(value)
    secretish = isinstance(value, Secret) or meta.get("secret")
    choices = meta.get("choices")
    if choices is not None and isinstance(choices, (list, tuple)) and inner not in choices:
        raise error(
            "HED-MODEL-0005",
            title="Value not in choices",
            explanation=(
                f"Field {field_name!r} value is not among the allowed choices."
                if not secretish
                else f"Field {field_name!r} failed choices validation."
            ),
            remediation="Pass one of the declared choices.",
        )
    min_length = meta.get("min_length")
    if (
        min_length is not None
        and isinstance(min_length, (int, float))
        and isinstance(inner, Sized)
        and len(inner) < int(min_length)
    ):
        raise error(
            "HED-MODEL-0006",
            title="Value length below minimum",
            explanation=f"Field {field_name!r} does not meet min_length={min_length}.",
            remediation="Provide a longer value.",
        )
    max_length = meta.get("max_length")
    if (
        max_length is not None
        and isinstance(max_length, (int, float))
        and isinstance(inner, Sized)
        and len(inner) > int(max_length)
    ):
        raise error(
            "HED-MODEL-0006",
            title="Value length above maximum",
            explanation=f"Field {field_name!r} exceeds max_length={max_length}.",
            remediation="Provide a shorter value.",
        )
    pattern = meta.get("pattern")
    if (
        pattern is not None
        and isinstance(pattern, str)
        and isinstance(inner, str)
        and re.search(pattern, inner) is None
    ):
        raise error(
            "HED-MODEL-0006",
            title="Value does not match pattern",
            explanation=f"Field {field_name!r} does not match the required pattern.",
            remediation="Correct the value format.",
        )


class Model(BaseModel):
    """Portable domain data used by UI contracts."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        arbitrary_types_allowed=True,
        validate_assignment=True,
    )

    _hedron_role: ClassVar[str] = "model"

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        try:
            from typing import get_type_hints

            hints = get_type_hints(cls)
        except Exception:  # noqa: BLE001
            hints = {
                k: v
                for k, v in getattr(cls, "__annotations__", {}).items()
                if not isinstance(v, str)
            }
        for name, hint in hints.items():
            if name.startswith("_"):
                continue
            if not _is_supported_annotation(hint):
                raise error(
                    "HED-MODEL-0003",
                    title="Unsupported model field type",
                    explanation=f"Field {cls.__name__}.{name} uses unsupported type {hint!r}.",
                    remediation=(
                        "Use Hedron-supported primitives, enums, models, "
                        "SafeUrl, Secret, or TrustedHtml."
                    ),
                )

    @model_validator(mode="after")
    def _validate_hedron_constraints(self) -> Model:
        for name, field_info in self.__class__.model_fields.items():
            meta = hedron_meta(field_info)
            if not meta:
                continue
            value = getattr(self, name)
            try:
                _apply_hedron_constraints(name, value, meta)
            except HedronError:
                raise
        return self

    @model_serializer(mode="wrap")
    def _serialize_redacted(self, serializer: Any) -> Any:
        data = serializer(self)
        if not isinstance(data, dict):
            return data
        result: dict[str, object] = {}
        for key, value in data.items():
            field_info: FieldInfo | None = self.__class__.model_fields.get(key)
            meta = hedron_meta(field_info) if field_info is not None else {}
            attr = getattr(self, key, value)
            if isinstance(attr, Secret) or meta.get("secret"):
                result[key] = "***"
            else:
                result[key] = redact_value(value)
        return result


class Props(Model):
    """Component construction input; never automatically exposed as HTTP input."""

    _hedron_role: ClassVar[str] = "props"


class FormModel(Model):
    """Client-submitted form or action input with presentation metadata."""

    _hedron_role: ClassVar[str] = "form"


class EventPayload(Model):
    """Typed custom-event data crossing a browser/server boundary."""

    _hedron_role: ClassVar[str] = "event"
