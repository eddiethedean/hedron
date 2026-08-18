"""Generate native Form markup from a compiled FormBody inventory."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import Enum
from typing import Any, Literal, cast, get_args, get_origin

from hedron.type_authoring.markers import CONTROL_KINDS, Control
from hedron.type_authoring.normalize import CompiledTypeHandler, FieldRecord
from hedron_core.builtins.forms import (
    CsrfField,
    Form,
    FormErrors,
    FormField,
    Select,
    SubmitButton,
    TextArea,
    TextInput,
)
from hedron_core.builtins.forms_extra import DateInput, DateTimeInput, NumberInput, TimeInput
from hedron_core.codes import HED_TYPE_0005
from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import error
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.rendering import active_render_context

__all__ = ["generate_form"]

_PENDING_CSRF_TOKEN = "hedron-pending-csrf"


class _RenderTimeCsrfProps(Props):
    pass


class _RenderTimeCsrfField(Component[_RenderTimeCsrfProps]):
    """Defer CSRF resolution until ``CsrfField.render()`` sees a live context."""

    props_type = _RenderTimeCsrfProps

    def __init__(self) -> None:
        super().__init__(_RenderTimeCsrfProps())

    def render(self) -> NodeLike:
        ctx = active_render_context()
        if ctx is not None and ctx.csrf_token:
            return CsrfField()
        return CsrfField(token=_PENDING_CSRF_TOKEN)


def generate_form(
    compiled: CompiledTypeHandler,
    *,
    action: object,
    value: object | Mapping[str, object] | None = None,
    errors: Sequence[object] = (),
    submit_label: str = "Submit",
    controls: Mapping[str, NodeLike | Control] | None = None,
    fallback: str | None = None,
    enhance: Literal["native", "elements"] = "native",
    **safe_form_attrs: object,
) -> Form:
    if compiled.model_type is None or not any(
        item == "FormBody" for item in (compiled.schema.boundary_sources if compiled.schema else ())
    ):
        raise error(
            HED_TYPE_0005,
            title="form() requires a FormBody boundary",
            explanation="ActionHandle.form() is only available for opted-in FormBody commands.",
            remediation="Mark one command parameter with FormBody() or use Form(action=handle).",
        )
    overrides = dict(controls or {})
    current = _value_map(value)
    error_map, model_errors = _error_map(errors)
    nodes: list[NodeLike] = []
    # Resolve the token at render time. Page handlers call form() before
    # RenderContext exists; baking token= here freezes the placeholder.
    nodes.append(_RenderTimeCsrfField())
    form_errors = model_errors + list(error_map.values())
    if form_errors:
        nodes.append(FormErrors(form_errors))
    for record in compiled.fields:
        override = overrides.get(record.name) or overrides.get(record.path)
        if record.disposition == "override_only" and override is None:
            raise error(
                HED_TYPE_0005,
                title="Override-only field needs an explicit control",
                explanation=f"Field {record.path!r} cannot be auto-generated.",
                remediation="Pass controls={...} or build Form(action=handle) manually.",
            )
        if record.disposition == "rejected":
            raise error(
                HED_TYPE_0005,
                title="Rejected field cannot be generated",
                explanation=f"Field {record.path!r} is outside the supported inventory.",
                remediation="Remove the field or replace the whole form.",
            )
        if isinstance(override, Control):
            control_node = _native_control(record, current, control=override)
        elif override is not None:
            control_node = override
        else:
            control_node = _native_control(record, current, control=None)
        if enhance == "elements" and override is None:
            control_node = _maybe_enhance(record, control_node, current)
        retained = current.get(record.name)
        if record.sensitive or record.control_kind == "password":
            retained = None
        err = error_map.get(record.name) or error_map.get(record.path)
        nodes.append(
            FormField(
                name=record.name,
                label=_label(record),
                control=control_node,
                required=record.required,
                help=_help(record),
                error=err,
            )
        )
        del retained
    nodes.append(SubmitButton(submit_label))
    attrs = {key: value for key, value in safe_form_attrs.items() if key.isidentifier()}
    if compiled.form_encoding == "multipart":
        attrs.setdefault("enctype", "multipart/form-data")
    if fallback:
        attrs.setdefault("data-hedron-fallback", fallback)
    return Form(*nodes, action=cast("Any", action), **cast("Any", attrs))


def _value_map(value: object | Mapping[str, object] | None) -> dict[str, object]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    dump = getattr(value, "model_dump", None)
    if callable(dump):
        dumped = dump(mode="python")
        if isinstance(dumped, Mapping):
            return dict(dumped)
    return {}


def _error_map(errors: Sequence[object]) -> tuple[dict[str, str], list[str]]:
    out: dict[str, str] = {}
    model_level: list[str] = []
    for item in errors:
        loc: object
        msg: object
        if isinstance(item, Mapping):
            loc = item.get("loc") or item.get("path")
            msg = item.get("msg") or item.get("message") or item
        else:
            loc = getattr(item, "loc", None) or getattr(item, "path", None)
            msg = getattr(item, "msg", None) or getattr(item, "message", item)
        if isinstance(loc, Sequence) and not isinstance(loc, (str, bytes)):
            key = ".".join(str(part) for part in loc if part not in {None, "body"})
        else:
            key = str(loc or "")
        if key:
            out[key] = str(msg)
        else:
            model_level.append(str(msg))
    return out, model_level


def _label(record: FieldRecord) -> str:
    if record.control_kind:
        return record.name.replace("_", " ").title()
    return record.name.replace("_", " ").title()


def _help(record: FieldRecord) -> str | None:
    return None


def _native_control(
    record: FieldRecord,
    current: Mapping[str, object],
    *,
    control: Control | None,
) -> NodeLike:
    kind = (
        (control.kind if control is not None else None)
        or record.control_kind
        or _default_kind(record)
    )
    if kind not in CONTROL_KINDS:
        raise error(
            HED_TYPE_0005,
            title="Unknown generated control kind",
            explanation=f"Cannot generate kind {kind!r} for {record.path!r}.",
            remediation="Pass an explicit Control from the closed kind inventory.",
        )
    raw = current.get(record.name)
    text = "" if raw is None or record.sensitive else str(raw)
    autocomplete = control.autocomplete if control is not None else None
    name = record.http_name
    if kind == "textarea":
        return TextArea(
            name,
            value=text,
            required=record.required,
            rows=control.rows if control is not None and control.rows else 4,
        )
    if kind == "number":
        return NumberInput(name, value=raw if isinstance(raw, (int, float)) else text or None)
    if kind == "checkbox":
        from hedron_core.builtins.forms import Checkbox

        return Checkbox(name, _label(record), checked=bool(raw))
    if kind in {"select", "radio"}:
        options = _enum_options(record.annotation)
        if not options:
            raise error(
                HED_TYPE_0005,
                title="Choice control has no options",
                explanation=f"Field {record.path!r} needs a Literal/Enum for select/radio.",
                remediation="Use an enum, Literal, or an explicit control override.",
            )
        if kind == "radio":
            from hedron_core.builtins.forms import RadioGroup

            return RadioGroup(name, _label(record), options, value=text or None)
        return Select(name, options, required=record.required, value=text or None)
    if kind == "date":
        return DateInput(name, value=text)
    if kind == "time":
        return TimeInput(name, value=text)
    if kind == "datetime-local":
        return DateTimeInput(name, value=text)
    if kind == "file":
        return html.input(type="file", name=name, required=record.required or None)
    input_type = "password" if kind == "password" else kind if kind in {"email", "url"} else "text"
    return TextInput(
        name,
        value="" if kind == "password" else text,
        required=record.required,
        type=input_type,  # type: ignore[arg-type]
        autocomplete=autocomplete,
    )


def _maybe_enhance(
    record: FieldRecord,
    native: NodeLike,
    current: Mapping[str, object],
) -> NodeLike:
    try:
        from hedron_elements.schema import enhanced_control
    except ImportError:
        return native
    kind = record.control_kind or _default_kind(record)
    return enhanced_control(  # type: ignore[return-value]
        kind,
        native,
        name=record.http_name,
        value=current.get(record.name, ""),
        options=_enum_options(record.annotation),
    )


def _default_kind(record: FieldRecord) -> str:
    if record.is_file:
        return "file"
    if record.sensitive:
        return "password"
    annotation = record.annotation
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin is not None and str(origin).endswith("Union"):
        non_none = [item for item in args if item is not type(None)]
        annotation = non_none[0] if len(non_none) == 1 else annotation
    if annotation is bool:
        return "checkbox"
    if annotation in {int, float}:
        return "number"
    from datetime import date, datetime, time

    if annotation is date:
        return "date"
    if annotation is time:
        return "time"
    if annotation is datetime:
        return "datetime-local"
    if origin is Literal or (isinstance(annotation, type) and issubclass(annotation, Enum)):
        return "select"
    return "text"


def _enum_options(annotation: object) -> list[tuple[str, str]]:
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin is Literal:
        return [(str(item), str(item)) for item in args]
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        return [
            (item.value if isinstance(item.value, str) else item.name, item.name)
            for item in annotation
        ]
    return []
