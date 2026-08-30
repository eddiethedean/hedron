"""FastAPI-oriented form widgets."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, ClassVar, Literal, cast

from hedron.builtins.hx import safe_target
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.htmx.attrs import HtmxAttrs
from hedron_core.models import FormModel, Props
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.typing_aliases import HtmlAttrMap, JsonValue

__all__ = ["AutoForm", "LoginCsrfField"]


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
        self.target = safe_target(target)

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
        htmx_attrs: HtmlAttrMap = {"aria-busy": "false"}
        if self.target:
            htmx_attrs.update(
                HtmxAttrs(
                    method=cast(
                        Literal["get", "post", "put", "patch", "delete"],
                        method,
                    ),
                    url=str(action_url),
                    target=self.target,
                    swap="innerHTML",
                    sync="closest form:drop",
                ).as_html_attrs()
            )

        from hedron_core.builtins.forms import Form

        return Form(
            *fields,
            action=action_url,
            method=method,
            **cast(Any, htmx_attrs),
        )
