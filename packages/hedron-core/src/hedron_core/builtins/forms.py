"""Form built-ins."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from hedron_core.component import Component
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.security import SafeUrl, UrlPurpose


class FormProps(Props):
    action: SafeUrl | None = None
    method: Literal["get", "post"] = "post"


class Form(Component[FormProps]):
    props_type = FormProps

    def __init__(
        self,
        *children: Any,
        action: SafeUrl | str | None = None,
        method: Literal["get", "post"] = "post",
        **kwargs: Any,
    ) -> None:
        url = None
        if action is not None:
            url = (
                action
                if isinstance(action, SafeUrl)
                else SafeUrl.parse(action, purpose=UrlPurpose.FORM_ACTION)
            )
        super().__init__(FormProps(action=url, method=method, **kwargs))
        self._children = children

    def render(self) -> Any:
        attrs: dict[str, Any] = {"method": self.props.method}
        if self.props.action is not None:
            attrs["action"] = self.props.action
        return html.form(*self._children, **attrs)


class LabelProps(Props):
    text: str
    for_: str | None = None


class Label(Component[LabelProps]):
    props_type = LabelProps

    def __init__(self, text: str, *, for_: str | None = None, **kwargs: Any) -> None:
        super().__init__(LabelProps(text=text, for_=for_, **kwargs))

    def render(self) -> Any:
        attrs: dict[str, Any] = {}
        if self.props.for_:
            attrs["for_"] = self.props.for_
        return html.label(self.props.text, **attrs)


class FormFieldProps(Props):
    name: str
    label: str
    help: str | None = None
    required: bool = False
    error: str | None = None


class FormField(Component[FormFieldProps]):
    props_type = FormFieldProps
    slots = {"control": "required"}

    def __init__(
        self,
        *,
        name: str,
        label: str,
        control: Any,
        help: str | None = None,
        required: bool = False,
        error: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            FormFieldProps(
                name=name,
                label=label,
                help=help,
                required=required,
                error=error,
                **kwargs,
            )
        )
        self._field_id = f"field-{name}"
        self._slot_values["control"] = self._bind_control(control)

    def _bind_control(self, control: Any) -> Any:
        """Force control id and propagate required / aria wiring."""
        field_id = self._field_id
        help_id = f"{field_id}-help" if self.props.help else None
        error_id = f"{field_id}-error" if self.props.error else None
        described_by = " ".join(x for x in (help_id, error_id) if x) or None

        # Prefer mutating known built-in controls via props reconstruction.
        if isinstance(control, Component):
            props = control.props
            updates: dict[str, Any] = {}
            if hasattr(props, "id"):
                updates["id"] = field_id
            if self.props.required and hasattr(props, "required"):
                updates["required"] = True
            if updates:
                new_props = props.model_copy(update=updates)
                control._props = new_props  # type: ignore[attr-defined]
            # Stash aria on a side channel consumed in render wrapper.
            control._hedron_aria = {  # type: ignore[attr-defined]
                "describedby": described_by,
                "invalid": "true" if self.props.error else None,
                "required": "true" if self.props.required else None,
            }
        return control

    def render(self) -> Any:
        help_id = f"{self._field_id}-help" if self.props.help else None
        error_id = f"{self._field_id}-error" if self.props.error else None
        control = self._slot_values["control"]
        aria = getattr(control, "_hedron_aria", {}) or {}

        # Wrap control so aria-* lands on the actual interactive element when possible.
        if isinstance(control, Component) and hasattr(control, "render"):
            rendered = control.render()
            control_node = self._apply_aria(rendered, aria)
        else:
            control_node = self._apply_aria(control, aria)

        parts: list[Any] = [
            Label(self.props.label, for_=self._field_id),
            control_node,
        ]
        if self.props.help:
            parts.append(html.p(self.props.help, id=help_id, class_="hedron-field-help"))
        if self.props.error:
            parts.append(
                html.p(
                    self.props.error,
                    id=error_id,
                    class_="hedron-field-error",
                    role="alert",
                )
            )
        return html.div(*parts, class_="hedron-form-field")

    def _apply_aria(self, node: Any, aria: dict[str, Any]) -> Any:
        from hedron_core.html import _NativeElement

        if not isinstance(node, _NativeElement):
            return node
        attrs = dict(node.attributes)
        if aria.get("describedby"):
            attrs["aria-describedby"] = aria["describedby"]
        if aria.get("invalid"):
            attrs["aria-invalid"] = aria["invalid"]
        if aria.get("required"):
            attrs["aria-required"] = aria["required"]
        # Rebuild with merged attributes through ElementNode path at render time.
        merged = _NativeElement(node.tag, node.children, {})
        merged.attributes = attrs
        return merged


class TextInputProps(Props):
    name: str
    id: str | None = None
    value: str = ""
    placeholder: str | None = None
    required: bool = False
    type: Literal["text", "email", "password", "search", "tel", "url"] = "text"
    autocomplete: str | None = None
    disabled: bool = False


class TextInput(Component[TextInputProps]):
    props_type = TextInputProps

    def __init__(
        self,
        name: str,
        *,
        id: str | None = None,
        value: str = "",
        placeholder: str | None = None,
        required: bool = False,
        type: Literal["text", "email", "password", "search", "tel", "url"] = "text",
        autocomplete: str | None = None,
        disabled: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            TextInputProps(
                name=name,
                id=id or f"field-{name}",
                value=value,
                placeholder=placeholder,
                required=required,
                type=type,
                autocomplete=autocomplete,
                disabled=disabled,
                **kwargs,
            )
        )

    def render(self) -> Any:
        attrs: dict[str, Any] = {
            "type": self.props.type,
            "name": self.props.name,
            "id": self.props.id,
            "value": self.props.value,
        }
        if self.props.placeholder:
            attrs["placeholder"] = self.props.placeholder
        if self.props.required:
            attrs["required"] = True
        if self.props.autocomplete:
            attrs["autocomplete"] = self.props.autocomplete
        if self.props.disabled:
            attrs["disabled"] = True
        return html.input(**attrs)


class TextAreaProps(Props):
    name: str
    id: str | None = None
    value: str = ""
    rows: int = 4
    required: bool = False
    placeholder: str | None = None


class TextArea(Component[TextAreaProps]):
    props_type = TextAreaProps

    def __init__(
        self,
        name: str,
        *,
        id: str | None = None,
        value: str = "",
        rows: int = 4,
        required: bool = False,
        placeholder: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            TextAreaProps(
                name=name,
                id=id or f"field-{name}",
                value=value,
                rows=rows,
                required=required,
                placeholder=placeholder,
                **kwargs,
            )
        )

    def render(self) -> Any:
        attrs: dict[str, Any] = {
            "name": self.props.name,
            "id": self.props.id,
            "rows": self.props.rows,
        }
        if self.props.required:
            attrs["required"] = True
        if self.props.placeholder:
            attrs["placeholder"] = self.props.placeholder
        return html.textarea(self.props.value, **attrs)


class SelectProps(Props):
    name: str
    id: str | None = None
    required: bool = False


class Select(Component[SelectProps]):
    props_type = SelectProps

    def __init__(
        self,
        name: str,
        options: Sequence[tuple[str, str]],
        *,
        id: str | None = None,
        required: bool = False,
        value: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            SelectProps(name=name, id=id or f"field-{name}", required=required, **kwargs)
        )
        self._options = tuple(options)
        self._value = value

    def render(self) -> Any:
        opts = []
        for val, label in self._options:
            attrs: dict[str, Any] = {"value": val}
            if self._value is not None and self._value == val:
                attrs["selected"] = True
            opts.append(html.option(label, **attrs))
        attrs: dict[str, Any] = {
            "name": self.props.name,
            "id": self.props.id,
        }
        if self.props.required:
            attrs["required"] = True
        return html.select(*opts, **attrs)


class CheckboxProps(Props):
    name: str
    label: str
    id: str | None = None
    checked: bool = False
    required: bool = False


class Checkbox(Component[CheckboxProps]):
    props_type = CheckboxProps

    def __init__(
        self,
        name: str,
        label: str,
        *,
        id: str | None = None,
        checked: bool = False,
        required: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            CheckboxProps(
                name=name,
                label=label,
                id=id or f"field-{name}",
                checked=checked,
                required=required,
                **kwargs,
            )
        )

    def render(self) -> Any:
        attrs: dict[str, Any] = {
            "type": "checkbox",
            "name": self.props.name,
            "id": self.props.id,
        }
        if self.props.checked:
            attrs["checked"] = True
        if self.props.required:
            attrs["required"] = True
        return html.div(
            html.input(**attrs),
            html.label(self.props.label, for_=self.props.id),
            class_="hedron-checkbox",
        )


class RadioGroupProps(Props):
    name: str
    legend: str
    required: bool = False


class RadioGroup(Component[RadioGroupProps]):
    props_type = RadioGroupProps

    def __init__(
        self,
        name: str,
        legend: str,
        options: Sequence[tuple[str, str]],
        *,
        value: str | None = None,
        required: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(RadioGroupProps(name=name, legend=legend, required=required, **kwargs))
        self._options = tuple(options)
        self._value = value

    def render(self) -> Any:
        inputs = []
        for val, label in self._options:
            fid = f"field-{self.props.name}-{val}"
            attrs: dict[str, Any] = {
                "type": "radio",
                "name": self.props.name,
                "id": fid,
                "value": val,
            }
            if self._value == val:
                attrs["checked"] = True
            if self.props.required:
                attrs["required"] = True
            inputs.append(
                html.div(
                    html.input(**attrs),
                    html.label(label, for_=fid),
                    class_="hedron-radio",
                )
            )
        return html.fieldset(html.legend(self.props.legend), *inputs)


class SubmitButtonProps(Props):
    label: str = "Submit"
    disabled: bool = False


class SubmitButton(Component[SubmitButtonProps]):
    props_type = SubmitButtonProps

    def __init__(self, label: str = "Submit", *, disabled: bool = False, **kwargs: Any) -> None:
        super().__init__(SubmitButtonProps(label=label, disabled=disabled, **kwargs))

    def render(self) -> Any:
        return html.button(
            self.props.label,
            type="submit",
            disabled=self.props.disabled or None,
            class_="hedron-button hedron-button-primary",
        )


class FormErrorsProps(Props):
    errors: tuple[str, ...]


class FormErrors(Component[FormErrorsProps]):
    props_type = FormErrorsProps

    def __init__(self, errors: Sequence[str], **kwargs: Any) -> None:
        super().__init__(FormErrorsProps(errors=tuple(errors), **kwargs))

    def render(self) -> Any:
        if not self.props.errors:
            return None
        return html.div(
            html.ul(*[html.li(e) for e in self.props.errors]),
            class_="hedron-form-errors",
            role="alert",
        )
