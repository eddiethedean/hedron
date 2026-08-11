"""Form built-ins."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar, Literal

from hedron_core.builtins._base import class_names, collect_children, dom_id_part
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.htmx_contract import safe_css_selector, safe_hx_swap
from hedron_core.models import Props
from hedron_core.rendering import active_render_context
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.typing_aliases import HtmlAttrValue


def _safe_optional_selector(value: str | None, *, label: str) -> str | None:
    if value is None or value == "":
        return None
    if not safe_css_selector(value):
        raise ValueError(f"Unsafe HTMX {label} selector: {value!r}")
    return value


@dataclass(frozen=True, slots=True)
class Hx:
    """First-class HTMX options for ``Form`` (FORM-022)."""

    target: str | None = None
    swap: str = "outerHTML"
    select: str | None = None
    select_oob: str | None = None
    push_url: bool | str = False
    disabled_elt: str | None = None
    indicator: str | None = None
    method: Literal["get", "post", "put", "patch", "delete"] | None = None
    url: str | None = None

    def as_html_attrs(self) -> dict[str, HtmlAttrValue]:
        target = _safe_optional_selector(self.target, label="target")
        select = _safe_optional_selector(self.select, label="select")
        select_oob = _safe_optional_selector(self.select_oob, label="select-oob")
        if select_oob is not None:
            from hedron_core.interaction import unparsed_select_oob_tokens

            unparsed = unparsed_select_oob_tokens(select_oob)
            if unparsed:
                tokens = ", ".join(sorted(unparsed))
                raise ValueError(
                    f"select_oob must use simple #id selectors only; unsupported token(s): {tokens}"
                )
        disabled_elt = _safe_optional_selector(self.disabled_elt, label="disabled-elt")
        indicator = _safe_optional_selector(self.indicator, label="indicator")
        if not safe_hx_swap(self.swap):
            raise ValueError(f"Unsafe HTMX swap value: {self.swap!r}")
        attrs: dict[str, HtmlAttrValue] = {}
        if self.method and self.url:
            safe = SafeUrl.parse(self.url, purpose=UrlPurpose.FORM_ACTION)
            attrs[f"hx-{self.method.lower()}"] = safe
        if target:
            attrs["hx-target"] = target
        if self.swap:
            attrs["hx-swap"] = self.swap
        if select:
            attrs["hx-select"] = select
        if select_oob:
            attrs["hx-select-oob"] = select_oob
        if self.push_url is True:
            attrs["hx-push-url"] = "true"
        elif isinstance(self.push_url, str) and self.push_url:
            safe_push = SafeUrl.parse(self.push_url, purpose=UrlPurpose.NAVIGATION)
            attrs["hx-push-url"] = safe_push
        if disabled_elt:
            attrs["hx-disabled-elt"] = disabled_elt
        if indicator:
            attrs["hx-indicator"] = indicator
        return attrs


_HX_SELECTOR_ATTRS = frozenset(
    {"hx-target", "hx-select", "hx-select-oob", "hx-indicator", "hx-disabled-elt"}
)


def _validate_hx_attr_map(attrs: dict[str, HtmlAttrValue]) -> None:
    """Reject unsafe HTMX selector/swap attrs whether they came from Hx or kwargs."""
    for key, value in attrs.items():
        if key in _HX_SELECTOR_ATTRS and isinstance(value, str) and value:
            label = key.removeprefix("hx-")
            if not safe_css_selector(value):
                raise ValueError(f"Unsafe HTMX {label} selector: {value!r}")
        if key == "hx-swap" and isinstance(value, str) and value and not safe_hx_swap(value):
            raise ValueError(f"Unsafe HTMX swap value: {value!r}")


class FormProps(Props):
    action: SafeUrl | None = None
    method: Literal["get", "post"] = "post"


class Form(Component[FormProps]):
    props_type = FormProps

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        action: SafeUrl | str | None = None,
        method: Literal["get", "post"] = "post",
        hx: Hx | None = None,
        **kwargs: HtmlAttrValue,
    ) -> None:
        url = None
        if action is not None:
            url = (
                action
                if isinstance(action, SafeUrl)
                else SafeUrl.parse(action, purpose=UrlPurpose.FORM_ACTION)
            )
        # Extra kwargs are native/HTMX attributes forwarded to the form element.
        extras = {k: v for k, v in kwargs.items() if k not in FormProps.model_fields}
        if hx is not None:
            # Validated Hx attrs win over raw kwargs (cannot override with unsafe strings).
            extras = {**extras, **hx.as_html_attrs()}
        _validate_hx_attr_map(extras)
        props_kwargs = {k: v for k, v in kwargs.items() if k in FormProps.model_fields}
        super().__init__(FormProps(action=url, method=method, **props_kwargs))
        self._children = collect_children(*nodes, children=children)
        self._html_attrs = extras

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {"method": self.props.method, **self._html_attrs}
        if self.props.action is not None:
            attrs["action"] = self.props.action
        return html.form(*self._children, **attrs)


class CsrfFieldProps(Props):
    name: str | None = None
    token: str | None = None


class CsrfField(Component[CsrfFieldProps]):
    """Hidden CSRF input wired to the active strategy / render context (FORM-022)."""

    props_type = CsrfFieldProps
    logical_name = "CsrfField"

    def __init__(
        self,
        *,
        name: str | None = None,
        token: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(CsrfFieldProps(name=name, token=token, **kwargs))

    def render(self) -> NodeLike:
        ctx = active_render_context()
        token = self.props.token
        name = self.props.name
        if token is None and ctx is not None:
            token = ctx.csrf_token
        if name is None:
            name = ctx.csrf_form_field if ctx is not None else "csrf_token"
        if not token:
            raise ValueError(
                "CsrfField requires token= or a RenderContext with csrf_token "
                "(FastAPI pages populate this automatically when CSRF is enabled)"
            )
        return html.input(type="hidden", name=name, value=token)


class LabelProps(Props):
    text: str
    for_: str | None = None


class Label(Component[LabelProps]):
    props_type = LabelProps

    def __init__(self, text: str, *, for_: str | None = None, **kwargs: object) -> None:
        super().__init__(LabelProps(text=text, for_=for_, **kwargs))

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {}
        if self.props.for_:
            attrs["for_"] = self.props.for_
        return html.label(self.props.text, **attrs)


class FormFieldProps(Props):
    name: str
    label: str
    id: str | None = None
    help: str | None = None
    required: bool = False
    error: str | None = None


class FormField(Component[FormFieldProps]):
    props_type = FormFieldProps
    slots: ClassVar[dict[str, str]] = {"control": "required"}

    def __init__(
        self,
        *,
        name: str,
        label: str,
        control: NodeLike,
        id: str | None = None,
        help: str | None = None,
        required: bool = False,
        error: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            FormFieldProps(
                name=name,
                label=label,
                id=id,
                help=help,
                required=required,
                error=error,
                **kwargs,
            )
        )
        self._slot_values["control"] = control

    def _bind_control(self, control: NodeLike, *, field_id: str) -> NodeLike:
        """Bind control id / required via a copied control; never mutate shared props."""
        help_id = f"{field_id}-help" if self.props.help else None
        error_id = f"{field_id}-error" if self.props.error else None
        described_by = " ".join(x for x in (help_id, error_id) if x) or None
        aria: dict[str, HtmlAttrValue] = {
            "describedby": described_by,
            "invalid": "true" if self.props.error else None,
            "required": "true" if self.props.required else None,
        }

        if isinstance(control, Component):
            props = control.props
            updates: dict[str, object] = {}
            fields = props.__class__.model_fields
            # Always force the label's for= target onto the control when possible.
            if "id" in fields:
                updates["id"] = field_id
            if self.props.required and "required" in fields:
                updates["required"] = True
            if "aria_describedby" in fields:
                existing = getattr(props, "aria_describedby", None)
                if described_by and existing:
                    updates["aria_describedby"] = f"{existing} {described_by}".strip()
                elif described_by:
                    updates["aria_describedby"] = described_by
                # Preserve caller aria when FormField has no help/error.
            if "aria_invalid" in fields and aria["invalid"] is not None:
                updates["aria_invalid"] = aria["invalid"]
            if "aria_required" in fields and aria["required"] is not None:
                updates["aria_required"] = aria["required"]
            new_props = props.model_copy(update=updates) if updates else props
            # Reconstruct a shallow copy of the control with updated props.
            bound = control.__class__.__new__(control.__class__)
            Component.__init__(bound, new_props)
            # Preserve non-props instance state used by built-ins (options, etc.).
            for attr_name, attr_value in vars(control).items():
                if attr_name in {"_props", "_children", "_slot_values", "_key"}:
                    continue
                setattr(bound, attr_name, attr_value)
            bound._children = control._children
            bound._slot_values = dict(control._slot_values)
            bound._key = control._key
            # Prefer returning the Component so identity/cycle checks still run.
            # Only fall back to HTML attribute merge when the control has no id/aria props.
            applied_via_props = "id" in fields and any(
                name in fields for name in ("aria_describedby", "aria_invalid", "aria_required")
            )
            needs_html_merge = ("id" not in fields) or (
                not any(
                    name in fields for name in ("aria_describedby", "aria_invalid", "aria_required")
                )
                and any(aria.values())
            )
            if needs_html_merge and not applied_via_props:
                node: NodeLike = bound
                while isinstance(node, Component):
                    node = node.render()
                return self._apply_aria(node, aria, element_id=field_id)
            return bound
        return self._apply_aria(control, aria, element_id=field_id)

    def render(self) -> NodeLike:
        field_id = self.props.id or (
            f"field-{dom_id_part(self.props.name)}-{self.render_instance_id()[2:10]}"
        )
        help_id = f"{field_id}-help" if self.props.help else None
        error_id = f"{field_id}-error" if self.props.error else None
        control = self._bind_control(self._slot_values["control"], field_id=field_id)

        skip_outer_label = isinstance(control, Checkbox) or isinstance(
            self._slot_values["control"], Checkbox
        )

        parts: list[NodeLike] = []
        if not skip_outer_label:
            parts.append(Label(self.props.label, for_=field_id))
        # Keep the bound component in the tree so it receives normal validation,
        # identity tracking, cycle detection, and renderer diagnostics.
        parts.append(control)
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

    def _apply_aria(
        self, node: NodeLike, aria: dict[str, HtmlAttrValue], *, element_id: str | None = None
    ) -> NodeLike:
        from hedron_core.html import _NativeElement

        if not isinstance(node, _NativeElement):
            return node

        def merge_attrs(el: _NativeElement) -> _NativeElement:
            attrs = dict(el.attributes)
            if element_id is not None:
                attrs["id"] = element_id
            if aria.get("describedby"):
                attrs["aria-describedby"] = aria["describedby"]
            if aria.get("invalid"):
                attrs["aria-invalid"] = aria["invalid"]
            if aria.get("required"):
                attrs["aria-required"] = aria["required"]
            return _NativeElement(el.tag, el.children, attrs)

        # Prefer applying aria to the interactive control inside wrappers (e.g. Checkbox).
        if node.tag == "div" and node.children:
            new_children = []
            applied = False
            for child in node.children:
                if (
                    not applied
                    and isinstance(child, _NativeElement)
                    and child.tag in {"input", "select", "textarea", "button"}
                ):
                    new_children.append(merge_attrs(child))
                    applied = True
                else:
                    new_children.append(child)
            if applied:
                return _NativeElement(node.tag, tuple(new_children), dict(node.attributes))
        if node.tag in {"input", "select", "textarea", "button"}:
            return merge_attrs(node)
        return merge_attrs(node)


class TextInputProps(Props):
    name: str
    id: str | None = None
    value: str = ""
    placeholder: str | None = None
    required: bool = False
    type: Literal["text", "email", "password", "search", "tel", "url"] = "text"
    autocomplete: str | None = None
    disabled: bool = False
    aria_describedby: str | None = None
    aria_invalid: str | None = None
    aria_required: str | None = None
    class_: str | None = None


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
        aria_describedby: str | None = None,
        aria_invalid: str | None = None,
        aria_required: str | None = None,
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            TextInputProps(
                name=name,
                id=id or f"field-{dom_id_part(name)}",
                value=value,
                placeholder=placeholder,
                required=required,
                type=type,
                autocomplete=autocomplete,
                disabled=disabled,
                aria_describedby=aria_describedby,
                aria_invalid=aria_invalid,
                aria_required=aria_required,
                class_=class_,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {
            "type": self.props.type,
            "name": self.props.name,
            "id": self.props.id,
            "value": self.props.value,
        }
        if self.props.class_:
            attrs["class_"] = class_names("hedron-text-input", self.props.class_)
        if self.props.placeholder:
            attrs["placeholder"] = self.props.placeholder
        if self.props.required:
            attrs["required"] = True
        if self.props.autocomplete:
            attrs["autocomplete"] = self.props.autocomplete
        if self.props.disabled:
            attrs["disabled"] = True
        attrs["aria"] = {
            "describedby": self.props.aria_describedby,
            "invalid": self.props.aria_invalid,
            "required": self.props.aria_required,
        }
        return html.input(**attrs)


class TextAreaProps(Props):
    name: str
    id: str | None = None
    value: str = ""
    rows: int = 4
    required: bool = False
    placeholder: str | None = None
    aria_describedby: str | None = None
    aria_invalid: str | None = None
    aria_required: str | None = None
    class_: str | None = None


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
        aria_describedby: str | None = None,
        aria_invalid: str | None = None,
        aria_required: str | None = None,
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            TextAreaProps(
                name=name,
                id=id or f"field-{dom_id_part(name)}",
                value=value,
                rows=rows,
                required=required,
                placeholder=placeholder,
                aria_describedby=aria_describedby,
                aria_invalid=aria_invalid,
                aria_required=aria_required,
                class_=class_,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {
            "name": self.props.name,
            "id": self.props.id,
            "rows": self.props.rows,
        }
        if self.props.class_:
            attrs["class_"] = class_names("hedron-textarea", self.props.class_)
        if self.props.required:
            attrs["required"] = True
        if self.props.placeholder:
            attrs["placeholder"] = self.props.placeholder
        attrs["aria"] = {
            "describedby": self.props.aria_describedby,
            "invalid": self.props.aria_invalid,
            "required": self.props.aria_required,
        }
        return html.textarea(self.props.value, **attrs)


class SelectProps(Props):
    name: str
    id: str | None = None
    required: bool = False
    aria_describedby: str | None = None
    aria_invalid: str | None = None
    aria_required: str | None = None
    class_: str | None = None


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
        aria_describedby: str | None = None,
        aria_invalid: str | None = None,
        aria_required: str | None = None,
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            SelectProps(
                name=name,
                id=id or f"field-{dom_id_part(name)}",
                required=required,
                aria_describedby=aria_describedby,
                aria_invalid=aria_invalid,
                aria_required=aria_required,
                class_=class_,
                **kwargs,
            )
        )
        self._options = tuple(options)
        self._value = value

    def render(self) -> NodeLike:
        opts = []
        for val, label in self._options:
            attrs: dict[str, HtmlAttrValue] = {"value": val}
            if self._value is not None and self._value == val:
                attrs["selected"] = True
            opts.append(html.option(label, **attrs))
        attrs: dict[str, HtmlAttrValue] = {
            "name": self.props.name,
            "id": self.props.id,
        }
        if self.props.class_:
            attrs["class_"] = class_names("hedron-select", self.props.class_)
        if self.props.required:
            attrs["required"] = True
        attrs["aria"] = {
            "describedby": self.props.aria_describedby,
            "invalid": self.props.aria_invalid,
            "required": self.props.aria_required,
        }
        return html.select(*opts, **attrs)


class CheckboxProps(Props):
    name: str
    label: str
    id: str | None = None
    checked: bool = False
    required: bool = False
    aria_describedby: str | None = None
    aria_invalid: str | None = None
    aria_required: str | None = None
    class_: str | None = None


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
        aria_describedby: str | None = None,
        aria_invalid: str | None = None,
        aria_required: str | None = None,
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            CheckboxProps(
                name=name,
                label=label,
                id=id or f"field-{dom_id_part(name)}",
                checked=checked,
                required=required,
                aria_describedby=aria_describedby,
                aria_invalid=aria_invalid,
                aria_required=aria_required,
                class_=class_,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {
            "type": "checkbox",
            "name": self.props.name,
            "id": self.props.id,
        }
        if self.props.checked:
            attrs["checked"] = True
        if self.props.required:
            attrs["required"] = True
        attrs["aria"] = {
            "describedby": self.props.aria_describedby,
            "invalid": self.props.aria_invalid,
            "required": self.props.aria_required,
        }
        return html.div(
            html.input(**attrs),
            html.label(self.props.label, for_=self.props.id),
            class_=class_names("hedron-checkbox", self.props.class_),
        )


class RadioGroupProps(Props):
    name: str
    legend: str
    id: str | None = None
    required: bool = False


class RadioGroup(Component[RadioGroupProps]):
    props_type = RadioGroupProps

    def __init__(
        self,
        name: str,
        legend: str,
        options: Sequence[tuple[str, str]],
        *,
        id: str | None = None,
        value: str | None = None,
        required: bool = False,
        **kwargs: object,
    ) -> None:
        super().__init__(
            RadioGroupProps(name=name, legend=legend, id=id, required=required, **kwargs)
        )
        self._options = tuple(options)
        self._value = value

    def render(self) -> NodeLike:
        inputs = []
        group_id = self.props.id or (
            f"field-{dom_id_part(self.props.name)}-{self.render_instance_id()[2:10]}"
        )
        for index, (val, label) in enumerate(self._options):
            fid = f"{group_id}-{index}"
            attrs: dict[str, HtmlAttrValue] = {
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
        return html.fieldset(
            html.legend(self.props.legend),
            *inputs,
            id=group_id,
        )


class SubmitButtonProps(Props):
    label: str = "Submit"
    disabled: bool = False
    class_: str | None = None


class SubmitButton(Component[SubmitButtonProps]):
    props_type = SubmitButtonProps

    def __init__(
        self,
        label: str = "Submit",
        *,
        disabled: bool = False,
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(SubmitButtonProps(label=label, disabled=disabled, class_=class_, **kwargs))

    def render(self) -> NodeLike:
        return html.button(
            self.props.label,
            type="submit",
            disabled=self.props.disabled or None,
            class_=class_names("hedron-button hedron-button-primary", self.props.class_),
        )


class FormErrorsProps(Props):
    errors: tuple[str, ...]


class FormErrors(Component[FormErrorsProps]):
    props_type = FormErrorsProps

    def __init__(self, errors: Sequence[str], **kwargs: object) -> None:
        super().__init__(FormErrorsProps(errors=tuple(errors), **kwargs))

    def render(self) -> NodeLike:
        if not self.props.errors:
            return None
        return html.div(
            html.ul(*[html.li(e) for e in self.props.errors]),
            class_="hedron-form-errors",
            role="alert",
        )
