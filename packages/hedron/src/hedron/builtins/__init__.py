"""Phase 0.2 FastAPI interaction built-ins."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, ClassVar

from hedron.routing.reverse import ComponentRef
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import FormModel, Props
from hedron_core.security import SafeUrl, UrlPurpose

__all__ = [
    "AutoForm",
    "ErrorState",
    "Lazy",
    "Loading",
    "Pagination",
    "RefreshButton",
    "action_attrs",
]


def action_attrs(
    ref: ComponentRef,
    *,
    include_csrf: bool = False,
    csrf_token: str | None = None,
) -> dict[str, str]:
    attrs = ref.hx_attrs()
    if include_csrf and csrf_token:
        attrs["hx-headers"] = f'{{"X-CSRF-Token": "{csrf_token}"}}'
    return attrs


class RefreshButton(Component[Props]):
    logical_name: ClassVar[str | None] = "RefreshButton"
    distribution: ClassVar[str] = "hedron"

    def __init__(
        self,
        label: str = "Refresh",
        *,
        ref: ComponentRef | None = None,
        href: str | None = None,
        target: str | None = None,
        swap: str = "outerHTML",
    ) -> None:
        super().__init__(Props())
        self.label = label
        self.ref = ref
        self.href = href
        self.target = target
        self.swap = swap

    def render(self) -> NodeLike:
        attrs: dict[str, Any] = {"type": "button"}
        if self.ref is not None:
            attrs.update(self.ref.hx_attrs())
            if self.target:
                attrs["hx-target"] = self.target
            attrs["hx-swap"] = self.swap
        elif self.href:
            attrs["hx-get"] = self.href
            if self.target:
                attrs["hx-target"] = self.target
            attrs["hx-swap"] = self.swap
        return html.button(self.label, **attrs)


class Lazy(Component[Props]):
    logical_name: ClassVar[str | None] = "Lazy"
    distribution: ClassVar[str] = "hedron"

    def __init__(
        self,
        *,
        ref: ComponentRef,
        placeholder: NodeLike | None = None,
        target_id: str | None = None,
    ) -> None:
        super().__init__(Props())
        self.ref = ref
        self.placeholder = placeholder
        self.target_id = target_id or f"lazy-{ref.logical_id.split('.')[-1]}"

    def render(self) -> NodeLike:
        attrs = {
            "id": self.target_id,
            "hx-get": self.ref.path,
            "hx-trigger": "load",
            "hx-swap": "innerHTML",
            "aria-busy": "true",
            "aria-live": "polite",
        }
        body = self.placeholder if self.placeholder is not None else Loading("Loading…")
        return html.div(body, **attrs)


class Loading(Component[Props]):
    logical_name: ClassVar[str | None] = "Loading"
    distribution: ClassVar[str] = "hedron"

    def __init__(self, message: str = "Loading…") -> None:
        super().__init__(Props())
        self.message = message

    def render(self) -> NodeLike:
        return html.div(
            html.span(self.message),
            role="status",
            aria={"live": "polite", "busy": "true"},
            class_="hedron-loading",
        )


class ErrorState(Component[Props]):
    logical_name: ClassVar[str | None] = "ErrorState"
    distribution: ClassVar[str] = "hedron"

    def __init__(
        self,
        message: str,
        *,
        retry_href: str | None = None,
        retry_label: str = "Retry",
        target: str | None = None,
    ) -> None:
        super().__init__(Props())
        self.message = message
        self.retry_href = retry_href
        self.retry_label = retry_label
        self.target = target

    def render(self) -> NodeLike:
        children: list[NodeLike] = [
            html.p(self.message, role="alert"),
        ]
        if self.retry_href:
            attrs: dict[str, Any] = {
                "type": "button",
                "hx-get": self.retry_href,
                "hx-swap": "outerHTML",
            }
            if self.target:
                attrs["hx-target"] = self.target
            children.append(html.button(self.retry_label, **attrs))
        return html.div(*children, class_="hedron-error", role="group")


class Pagination(Component[Props]):
    logical_name: ClassVar[str | None] = "Pagination"
    distribution: ClassVar[str] = "hedron"

    def __init__(
        self,
        *,
        page: int,
        page_size: int,
        total: int,
        base_path: str,
        target: str | None = None,
    ) -> None:
        super().__init__(Props())
        self.page = page
        self.page_size = page_size
        self.total = total
        self.base_path = base_path
        self.target = target

    def render(self) -> NodeLike:
        pages = max(1, (self.total + self.page_size - 1) // self.page_size)
        links: list[NodeLike] = []
        for number in range(1, pages + 1):
            sep = "&" if "?" in self.base_path else "?"
            href = f"{self.base_path}{sep}page={number}"
            attrs: dict[str, Any] = {"href": href}
            if self.target:
                attrs.update({"hx-get": href, "hx-target": self.target, "hx-swap": "innerHTML"})
            label = f"Page {number}" + (" (current)" if number == self.page else "")
            links.append(html.a(str(number), **attrs, aria={"label": label}))
        return html.nav(*links, aria={"label": "Pagination"}, class_="hedron-pagination")


class AutoForm(Component[Props]):
    logical_name: ClassVar[str | None] = "AutoForm"
    distribution: ClassVar[str] = "hedron"

    def __init__(
        self,
        model: type[FormModel] | FormModel,
        *,
        action: str | SafeUrl,
        method: str = "post",
        csrf_token: str | None = None,
        values: Mapping[str, Any] | None = None,
        errors: Sequence[str] = (),
        submit_label: str = "Submit",
        target: str | None = None,
    ) -> None:
        super().__init__(Props())
        self.model_type = model if isinstance(model, type) else type(model)
        self.instance = model if not isinstance(model, type) else None
        self.action = action
        self.method = method.lower()
        self.csrf_token = csrf_token
        self.values = dict(values or {})
        self.errors = tuple(errors)
        self.submit_label = submit_label
        self.target = target

    def render(self) -> NodeLike:
        from hedron_core.builtins.forms import FormErrors, FormField, SubmitButton, TextInput

        action_url = (
            self.action
            if isinstance(self.action, SafeUrl)
            else SafeUrl.parse(str(self.action), purpose=UrlPurpose.FORM_ACTION)
        )
        fields: list[NodeLike] = []
        if self.errors:
            fields.append(FormErrors(self.errors))
        if self.csrf_token:
            fields.append(html.input(type="hidden", name="csrf_token", value=self.csrf_token))
        model_fields = getattr(self.model_type, "model_fields", {})
        for name, field_info in model_fields.items():
            if name.startswith("_"):
                continue
            title = getattr(field_info, "title", None) or name.replace("_", " ").title()
            current = self.values.get(name, "")
            if self.instance is not None:
                current = getattr(self.instance, name, current)
            required = bool(getattr(field_info, "is_required", lambda: False)())
            fields.append(
                FormField(
                    name=name,
                    label=title,
                    control=TextInput(name, value=str(current) if current is not None else ""),
                    required=required,
                )
            )
        fields.append(SubmitButton(self.submit_label))
        form_attrs: dict[str, Any] = {
            "action": action_url,
            "method": self.method,
        }
        if self.target:
            form_attrs["hx-post" if self.method == "post" else "hx-get"] = str(action_url)
            form_attrs["hx-target"] = self.target
            form_attrs["hx-swap"] = "innerHTML"
        # Use core Form for semantics.
        from hedron_core.builtins.forms import Form

        return Form(*fields, **form_attrs)
