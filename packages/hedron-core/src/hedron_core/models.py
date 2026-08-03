"""Hedron model bases backed by constrained Pydantic."""

from __future__ import annotations

import types
from collections.abc import Callable, Mapping
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated, Any, ClassVar, Literal, Union, get_args, get_origin

from pydantic import BaseModel, ConfigDict, model_serializer
from pydantic.fields import FieldInfo

from hedron_core.diagnostics import error
from hedron_core.field import hedron_meta
from hedron_core.security import SafeUrl, Secret, TrustedHtml, redact_value

_PRIMITIVES = {str, int, float, bool, bytes, Decimal, date, datetime, type(None)}


def _is_supported_annotation(annotation: Any, *, depth: int = 0) -> bool:
    if depth > 8:
        return False
    if isinstance(annotation, str):
        return True  # forward reference; validated later
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is None:
        if annotation in _PRIMITIVES:
            return True
        if isinstance(annotation, type):
            if issubclass(annotation, Enum):
                return True
            if issubclass(annotation, (Model, SafeUrl, TrustedHtml)):
                return True
            if issubclass(annotation, Secret):
                return True
            if annotation in {object, type, Callable} or annotation.__name__ in {
                "Request",
                "Response",
            }:
                return False
        return False

    if origin in {Union, types.UnionType}:
        return all(_is_supported_annotation(a, depth=depth + 1) for a in args)
    if origin in {list, set, frozenset, tuple}:
        return all(_is_supported_annotation(a, depth=depth + 1) for a in args) if args else False
    if origin in {dict, Mapping}:
        if len(args) != 2:
            return False
        return args[0] is str and _is_supported_annotation(args[1], depth=depth + 1)
    if origin is Secret:
        return True
    if origin is Literal:
        return True
    if origin is Annotated:
        return _is_supported_annotation(args[0], depth=depth + 1) if args else False
    return False


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
        for name, hint in getattr(cls, "__annotations__", {}).items():
            if name.startswith("_"):
                continue
            if isinstance(hint, type) and (
                hint is object
                or hint is type
                or hint.__name__ in {"Request", "Response"}
                or (callable(hint) and hint is Callable)
            ):
                raise error(
                    "HED-MODEL-0003",
                    title="Unsupported model field type",
                    explanation=(f"Field {cls.__name__}.{name} uses unsupported type {hint!r}."),
                    remediation=(
                        "Use Hedron-supported primitives, enums, models, "
                        "SafeUrl, Secret, or TrustedHtml."
                    ),
                )

    @model_serializer(mode="wrap")
    def _serialize_redacted(self, serializer: Any) -> Any:
        data = serializer(self)
        if not isinstance(data, dict):
            return data
        result: dict[str, Any] = {}
        for key, value in data.items():
            field_info: FieldInfo | None = self.__class__.model_fields.get(key)
            meta = hedron_meta(field_info) if field_info is not None else {}
            attr = getattr(self, key, value)
            if isinstance(attr, Secret) or meta.get("secret"):
                result[key] = redact_value(attr) if isinstance(attr, Secret) else "***"
            else:
                result[key] = value
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
