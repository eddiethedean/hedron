"""Django Form / ModelForm / formset bridge to Hedron components."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from django.forms import BaseForm, BaseFormSet, BoundField
from django.http import HttpRequest
from django.middleware.csrf import get_token
from django.utils.html import format_html

from hedron_core import (
    Alert,
    Checkbox,
    FormErrors,
    FormField,
    RadioGroup,
    Select,
    Stack,
    TextArea,
    TextInput,
    html,
)
from hedron_core.component import NodeLike
from hedron_core.interaction import InteractionResult
from hedron_core.security import TrustedHtml

__all__ = [
    "csrf_hidden_input",
    "form_errors_node",
    "form_fields",
    "form_to_nodes",
    "formset_to_nodes",
    "validation_interaction",
]

_TextType = Literal["text", "email", "password", "search", "tel", "url"]


def csrf_hidden_input(request: HttpRequest) -> TrustedHtml:
    """Return a Django CSRF hidden input as trusted HTML for forms."""
    token = get_token(request)
    return TrustedHtml.reviewed(
        str(
            format_html(
                '<input type="hidden" name="csrfmiddlewaretoken" value="{}">',
                token,
            )
        ),
        source="django.middleware.csrf",
    )


def _widget_kind(bound: BoundField) -> str:
    widget = bound.field.widget
    input_type = getattr(widget, "input_type", None)
    name = type(widget).__name__.lower()
    if "radioselect" in name or "radio" in name:
        return "radio"
    if "clearablefile" in name or "file" in name or input_type == "file":
        return "file"
    if "number" in name or input_type == "number":
        return "number"
    if isinstance(input_type, str) and input_type:
        return input_type
    if "textarea" in name:
        return "textarea"
    if "select" in name:
        return "select"
    if "checkbox" in name:
        return "checkbox"
    if "password" in name:
        return "password"
    if "email" in name:
        return "email"
    return "text"


def _text_type(kind: str) -> _TextType:
    if kind in {"email", "password", "search", "tel", "url"}:
        return kind  # type: ignore[return-value]
    return "text"


def _choices(bound: BoundField) -> tuple[tuple[str, str], ...]:
    field = bound.field
    raw = getattr(field, "choices", None)
    if raw is None:
        return ()
    flat: list[tuple[str, str]] = []
    for entry in raw:
        if not entry:
            continue
        value, label = entry[0], entry[1]
        if isinstance(label, (list, tuple)):
            for sub_value, sub_label in label:
                flat.append((str(sub_value), str(sub_label)))
        else:
            flat.append((str(value), str(label)))
    return tuple(flat)


def form_fields(form: BaseForm) -> list[NodeLike]:
    """Render visible bound fields as Hedron form controls."""
    nodes: list[NodeLike] = []
    for bound in form:  # type: ignore[assignment]
        if not isinstance(bound, BoundField):
            continue
        if bound.is_hidden:
            nodes.append(html.raw(TrustedHtml.reviewed(str(bound), source="django.forms.hidden")))
            continue
        name = bound.html_name
        label = str(bound.label) if bound.label else bound.name
        value = bound.value()
        str_value = "" if value is None else str(value)
        error = "; ".join(str(e) for e in bound.errors) or None
        kind = _widget_kind(bound)
        control: NodeLike
        required = bool(getattr(bound.field, "required", False))
        if kind == "textarea":
            control = TextArea(name=name, value=str_value)
        elif kind == "select":
            control = Select(name=name, options=_choices(bound), value=str_value)
        elif kind == "radio":
            control = RadioGroup(
                name=name,
                legend=label,
                options=_choices(bound),
                value=str_value or None,
                required=required,
            )
        elif kind == "checkbox":
            # BoundField.value() may expose the widget's textual false value.
            checked = value is True or (
                isinstance(value, str) and value.strip().lower() in {"1", "true", "on", "yes"}
            )
            control = Checkbox(name=name, label=label, checked=checked)
        elif kind == "number":
            control = html.input(
                type="text",
                inputmode="decimal",
                name=name,
                id=f"field-{name}",
                value=str_value,
            )
        elif kind == "file":
            control = html.input(type="file", name=name, id=f"field-{name}")
        else:
            control = TextInput(name=name, value=str_value, type=_text_type(kind))
        nodes.append(
            FormField(
                name=name,
                label=label,
                control=control,
                error=error,
                required=required,
            )
        )
    return nodes


def form_errors_node(form: BaseForm) -> NodeLike | None:
    """Non-field errors as an accessible alert / FormErrors node."""
    non_field = [str(e) for e in form.non_field_errors()]
    if not non_field:
        return None
    return Stack(Alert("\n".join(non_field), tone="danger"), FormErrors(non_field))


def form_to_nodes(
    form: BaseForm,
    *,
    request: HttpRequest | None = None,
    include_csrf: bool = True,
) -> list[NodeLike]:
    """Full form body: optional CSRF, non-field errors, then fields."""
    nodes: list[NodeLike] = []
    if include_csrf and request is not None:
        nodes.append(html.raw(csrf_hidden_input(request)))
    err = form_errors_node(form)
    if err is not None:
        nodes.append(err)
    nodes.extend(form_fields(form))
    return nodes


def formset_to_nodes(
    formset: BaseFormSet,
    *,
    request: HttpRequest | None = None,
    include_csrf: bool = True,
) -> list[NodeLike]:
    """Render a formset management form + each form's fields."""
    nodes: list[NodeLike] = []
    if include_csrf and request is not None:
        nodes.append(html.raw(csrf_hidden_input(request)))
    nodes.append(
        html.raw(TrustedHtml.reviewed(str(formset.management_form), source="django.forms.formset"))
    )
    non_form = formset.non_form_errors()
    if non_form:
        nodes.append(Alert("\n".join(str(e) for e in non_form), tone="danger"))
    for form in formset:
        nodes.append(Stack(*form_to_nodes(form, request=None, include_csrf=False)))
    return nodes


def validation_interaction(
    form: BaseForm,
    *,
    request: HttpRequest | None = None,
    explanation: str = "django form validation",
    extra: Mapping[str, object] | None = None,
) -> InteractionResult:
    """Build an InteractionResult for invalid forms (HTMX and non-HTMX parity)."""
    del extra
    content = Stack(*form_to_nodes(form, request=request))
    return InteractionResult(content=content, explanation=explanation)
