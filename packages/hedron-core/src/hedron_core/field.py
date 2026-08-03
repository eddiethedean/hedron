"""Field metadata for Hedron models."""

from __future__ import annotations

from typing import Any

from pydantic import Field as PydanticField
from pydantic.fields import FieldInfo

from hedron_core.diagnostics import error


def Field(  # noqa: N802 — public API matches specification
    default: Any = ...,
    *,
    default_factory: Any = None,
    # Validation
    minimum: float | int | None = None,
    maximum: float | int | None = None,
    min_length: int | None = None,
    max_length: int | None = None,
    pattern: str | None = None,
    choices: list[Any] | tuple[Any, ...] | None = None,
    required: bool | None = None,
    # Presentation
    label: str | None = None,
    help: str | None = None,
    placeholder: str | None = None,
    display: str | None = None,
    autocomplete: str | None = None,
    format: str | None = None,
    # Access
    read_only: bool = False,
    hidden: bool = False,
    secret: bool = False,
    writable_policy: str | None = None,
    # Data
    key: str | None = None,
    sortable: bool = False,
    filterable: bool = False,
    editor: str | None = None,
    width: str | int | None = None,
    identity: bool = False,
    # Accessibility
    accessible_label: str | None = None,
    accessible_description: str | None = None,
    accessible_error: str | None = None,
    **extra: Any,
) -> Any:
    """Declare validation, presentation, access, data, and a11y metadata."""
    if read_only and writable_policy is not None:
        raise error(
            "HED-MODEL-0001",
            title="Contradictory field metadata",
            explanation="A field cannot be both read_only and have a writable_policy.",
            remediation="Remove one of read_only or writable_policy.",
        )
    if hidden and accessible_label is None and label is None:
        # Hidden fields may omit visible labels; ok.
        pass
    if secret and display == "plaintext":
        raise error(
            "HED-MODEL-0001",
            title="Contradictory field metadata",
            explanation="A secret field cannot use plaintext display.",
            remediation="Remove display='plaintext' or secret=True.",
        )
    if extra:
        raise error(
            "HED-MODEL-0002",
            title="Unsupported Field option",
            explanation=f"Unknown Field options: {sorted(extra)!r}",
            remediation="Use only documented Field metadata groups.",
        )

    ge = minimum
    le = maximum
    pydantic_kwargs: dict[str, Any] = {}
    if default_factory is not None:
        pydantic_kwargs["default_factory"] = default_factory
    elif default is not ...:
        pydantic_kwargs["default"] = default
    if ge is not None:
        pydantic_kwargs["ge"] = ge
    if le is not None:
        pydantic_kwargs["le"] = le
    if min_length is not None:
        pydantic_kwargs["min_length"] = min_length
    if max_length is not None:
        pydantic_kwargs["max_length"] = max_length
    if pattern is not None:
        pydantic_kwargs["pattern"] = pattern

    json_schema_extra = {
        "hedron": {
            "label": label,
            "help": help,
            "placeholder": placeholder,
            "display": display,
            "autocomplete": autocomplete,
            "format": format,
            "read_only": read_only,
            "hidden": hidden,
            "secret": secret,
            "writable_policy": writable_policy,
            "key": key,
            "sortable": sortable,
            "filterable": filterable,
            "editor": editor,
            "width": width,
            "identity": identity,
            "accessible_label": accessible_label,
            "accessible_description": accessible_description,
            "accessible_error": accessible_error,
            "choices": list(choices) if choices is not None else None,
            "required": required,
        }
    }
    pydantic_kwargs["json_schema_extra"] = json_schema_extra
    return PydanticField(**pydantic_kwargs)


def hedron_meta(info: FieldInfo) -> dict[str, Any]:
    extra = info.json_schema_extra
    if isinstance(extra, dict):
        meta = extra.get("hedron")
        if isinstance(meta, dict):
            return meta
    return {}
