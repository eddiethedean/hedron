"""Phase 0.2 FastAPI interaction built-ins."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import ClassVar, Literal

from hedron.htmx import _safe_css_selector
from hedron.routing.reverse import ComponentRef
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.interaction import FragmentRegion
from hedron_core.models import FormModel, Props
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.typing_aliases import HtmlAttrMap, JsonValue

__all__ = [
    "AutoForm",
    "ErrorState",
    "InfiniteScroll",
    "Lazy",
    "Loading",
    "LoginCsrfField",
    "Pagination",
    "Poll",
    "RefreshButton",
    "action_attrs",
    "oob_swap",
]


class LoginCsrfField(Component[Props]):
    """Hidden input for pre-auth login CSRF (not the post-auth ``CsrfField`` token).

    Use with :func:`hedron.security.issue_login_csrf` / :func:`validate_login_csrf`.
    Plain ``CsrfField`` embeds the active strategy / RenderContext token and will
    not validate against the login CSRF store.
    """

    logical_name: ClassVar[str | None] = "LoginCsrfField"
    distribution: ClassVar[str] = "hedron"

    def __init__(
        self,
        *,
        token: str | None = None,
        session: Mapping[str, object] | None = None,
        name: str | None = None,
    ) -> None:
        from hedron.security.login_csrf import LOGIN_CSRF_KEY, issue_login_csrf

        super().__init__(Props())
        if token is None:
            # issue_login_csrf accepts MutableMapping; Mapping is enough when token given.
            from collections.abc import MutableMapping

            if session is not None and isinstance(session, MutableMapping):
                token = issue_login_csrf(session)
            else:
                token = issue_login_csrf(None)
        self._token = token
        self._name = name or LOGIN_CSRF_KEY

    def render(self) -> NodeLike:
        return html.input(type="hidden", name=self._name, value=self._token)


def action_attrs(
    ref: ComponentRef,
    *,
    include_csrf: bool = False,
    csrf_token: str | None = None,
    csrf_header_name: str = "X-CSRF-Token",
) -> dict[str, str]:
    attrs = ref.hx_attrs()
    if include_csrf and csrf_token:
        attrs["hx-headers"] = json.dumps({csrf_header_name: csrf_token})
    return attrs


def oob_swap(
    element_id: str,
    content: NodeLike,
    *,
    swap: str = "innerHTML",
    tag: Literal["div", "section", "aside", "main", "nav"] = "div",
) -> NodeLike:
    """Mark a node for HTMX out-of-band swap via hx-swap-oob."""
    from hedron_core.interaction import oob_swap as core_oob_swap

    return core_oob_swap(element_id, content, swap=swap, tag=tag)


def _safe_target(target: str | None) -> str | None:
    if target is None:
        return None
    if not _safe_css_selector(target):
        raise ValueError(f"Unsafe HTMX target selector: {target!r}")
    return target


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
        self.target = _safe_target(target)
        self.swap = swap

    @classmethod
    def for_region(
        cls,
        region: FragmentRegion | str,
        *,
        href: str | None = None,
        label: str = "Refresh",
        ref: ComponentRef | None = None,
        swap: str = "outerHTML",
    ) -> RefreshButton:
        """Wire ``hx-target`` from a :class:`~hedron_core.interaction.FragmentRegion`."""
        target = region.selector if isinstance(region, FragmentRegion) else str(region)
        return cls(label, ref=ref, href=href, target=target, swap=swap)

    def render(self) -> NodeLike:
        attrs: HtmlAttrMap = {"type": "button"}
        if self.ref is not None:
            attrs.update(self.ref.hx_attrs())
            if self.target:
                attrs["hx-target"] = self.target
            attrs["hx-swap"] = self.swap
        elif self.href:
            attrs["hx-get"] = SafeUrl.parse(self.href, purpose=UrlPurpose.NAVIGATION)
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
        self.target_id = target_id

    def render(self) -> NodeLike:
        target_id = self.target_id or f"lazy-{self.render_instance_id()}"
        attrs: HtmlAttrMap = {
            "id": target_id,
            "hx-trigger": "load",
            "hx-swap": "innerHTML",
            "aria-busy": "true",
            "aria-live": "polite",
        }
        attrs.update(self.ref.hx_attrs())
        # Lazy container loads into itself.
        attrs["hx-target"] = f"#{target_id}"
        body = self.placeholder if self.placeholder is not None else Loading("Loading…")
        return html.div(body, **attrs)


class Poll(Component[Props]):
    """Interval-based HTMX refresh helper."""

    logical_name: ClassVar[str | None] = "Poll"
    distribution: ClassVar[str] = "hedron"

    def __init__(
        self,
        *,
        ref: ComponentRef,
        interval_ms: int = 5000,
        target_id: str | None = None,
        content: NodeLike | None = None,
    ) -> None:
        super().__init__(Props())
        self.ref = ref
        self.interval_ms = max(250, interval_ms)
        self.target_id = target_id
        self.content = content

    def render(self) -> NodeLike:
        target_id = self.target_id or f"poll-{self.render_instance_id()}"
        attrs: HtmlAttrMap = {
            "id": target_id,
            "hx-trigger": f"every {self.interval_ms}ms",
            "hx-swap": "innerHTML",
        }
        attrs.update(self.ref.hx_attrs())
        attrs["hx-target"] = f"#{target_id}"
        body = self.content if self.content is not None else Loading("Polling…")
        return html.div(body, **attrs)


class InfiniteScroll(Component[Props]):
    """Sentinel that loads the next page when revealed."""

    logical_name: ClassVar[str | None] = "InfiniteScroll"
    distribution: ClassVar[str] = "hedron"

    def __init__(
        self,
        *,
        ref: ComponentRef,
        target: str,
        swap: str = "beforeend",
    ) -> None:
        super().__init__(Props())
        self.ref = ref
        self.target = _safe_target(target)
        self.swap = swap

    def render(self) -> NodeLike:
        attrs: HtmlAttrMap = {
            "hx-trigger": "revealed",
            "hx-swap": self.swap,
        }
        attrs.update(self.ref.hx_attrs())
        if self.target:
            attrs["hx-target"] = self.target
        return html.div("Load more", **attrs, class_="hedron-infinite-scroll")


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
        self.target = _safe_target(target)

    def render(self) -> NodeLike:
        children: list[NodeLike] = [
            html.p(self.message, role="alert"),
        ]
        if self.retry_href:
            attrs: HtmlAttrMap = {
                "type": "button",
                "hx-get": SafeUrl.parse(self.retry_href, purpose=UrlPurpose.NAVIGATION),
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
        self.target = _safe_target(target)

    def render(self) -> NodeLike:
        pages = max(1, (self.total + self.page_size - 1) // self.page_size)
        links: list[NodeLike] = []
        for number in range(1, pages + 1):
            sep = "&" if "?" in self.base_path else "?"
            href_str = f"{self.base_path}{sep}page={number}"
            href = SafeUrl.parse(href_str, purpose=UrlPurpose.NAVIGATION)
            attrs: HtmlAttrMap = {"href": href}
            if self.target:
                attrs.update(
                    {
                        "hx-get": href,
                        "hx-target": self.target,
                        "hx-swap": "innerHTML",
                    }
                )
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
        csrf_form_field: str = "csrf_token",
        values: Mapping[str, JsonValue] | None = None,
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
        self.csrf_form_field = csrf_form_field
        self.values = dict(values or {})
        self.errors = tuple(errors)
        self.submit_label = submit_label
        self.target = _safe_target(target)

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
            from hedron_core.builtins.forms import CsrfField

            fields.append(CsrfField(name=self.csrf_form_field, token=self.csrf_token))
        elif self.method == "post":
            # Prefer RenderContext token when callers omit csrf_token= (FORM-022).
            from hedron_core.builtins.forms import CsrfField
            from hedron_core.rendering import active_render_context

            ctx = active_render_context()
            if ctx is not None and ctx.csrf_token:
                field_name = self.csrf_form_field or ctx.csrf_form_field or "csrf_token"
                fields.append(CsrfField(name=field_name))
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
        method = "post" if self.method == "post" else "get"
        htmx_attrs: HtmlAttrMap = {}
        if self.target:
            htmx_attrs["hx-post" if method == "post" else "hx-get"] = action_url
            htmx_attrs["hx-target"] = self.target
            htmx_attrs["hx-swap"] = "innerHTML"
            htmx_attrs["hx-sync"] = "closest form:drop"
            htmx_attrs["aria-busy"] = "false"
        from typing import Any, cast

        from hedron_core.builtins.forms import Form

        return Form(
            *fields,
            action=action_url,
            method=method,
            **cast(Any, htmx_attrs),
        )
