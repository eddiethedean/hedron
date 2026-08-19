"""Analysis workbench components for phase 0.16."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any, ClassVar, Literal

from pydantic import Field

from hedron_core.builtins._base import ElementProps, class_names, mark_data
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.security import SafeUrl, UrlPurpose

_ALLOWED_CODE_LANGUAGES = frozenset(
    {"python", "javascript", "typescript", "json", "html", "css", "sql", "markdown", "text"}
)


class DataExplorerFacet(Props):
    field: str
    label: str
    values: list[str] = Field(default_factory=list)


class DataExplorerProps(ElementProps):
    facets: list[DataExplorerFacet]
    name: str = "explorer"
    max_rows: int = 1000
    revision: str = "0"


class DataExplorer(Component[DataExplorerProps]):
    """Faceted explorer that emits a bounded TransformPlan — never collects distributed data."""

    props_type = DataExplorerProps
    logical_name = "DataExplorer"
    distribution = "hedron-extras"

    def __init__(
        self,
        facets: Sequence[DataExplorerFacet | Mapping[str, Any]],
        *,
        name: str = "explorer",
        max_rows: int = 1000,
        revision: str = "0",
        **kwargs: Any,
    ) -> None:
        parsed = [
            f if isinstance(f, DataExplorerFacet) else DataExplorerFacet.model_validate(f)
            for f in facets
        ]
        if max_rows < 1 or max_rows > 10_000:
            raise ValueError("DataExplorer max_rows must be between 1 and 10000")
        super().__init__(
            DataExplorerProps(
                facets=parsed, name=name, max_rows=max_rows, revision=revision, **kwargs
            )
        )

    def render(self) -> NodeLike:
        groups: list[NodeLike] = []
        for facet in self.props.facets:
            options = [html.option(v, value=v) for v in facet.values] or [
                html.option("(any)", value="")
            ]
            groups.append(
                html.label(
                    html.span(facet.label),
                    html.select(
                        *options,
                        name=f"{self.props.name}__{facet.field}",
                        data={"facet-field": facet.field},
                    ),
                )
            )
        groups.append(
            html.input(
                type="hidden",
                name=f"{self.props.name}__max_rows",
                value=str(self.props.max_rows),
            )
        )
        groups.append(
            html.input(
                type="hidden",
                name=f"{self.props.name}__revision",
                value=self.props.revision,
            )
        )
        groups.append(
            html.button(
                "Apply",
                type="submit",
                name=f"{self.props.name}__apply",
                value="1",
            )
        )
        groups.append(
            html.button(
                "Cancel",
                type="submit",
                name=f"{self.props.name}__cancel",
                value="1",
                data={"hedron-cancel": "true"},
            )
        )
        groups.append(
            html.button(
                "Export",
                type="submit",
                name=f"{self.props.name}__export",
                value="csv",
            )
        )
        return html.form(
            *groups,
            class_=class_names("hedron-data-explorer", self.props.class_),
            id=self.props.id,
            method="post",
            data={
                **mark_data(self.props.mark),
                "hedron-workbench": "data-explorer",
                "emits": "transform-plan",
                "max-rows": str(self.props.max_rows),
                "revision": self.props.revision,
                "collect-distributed": "never",
                "no-eval": "true",
            },
        )


class JSONEditorProps(ElementProps):
    value: str
    schema_text: str | None = None
    name: str = "json"
    max_chars: int = 200_000
    read_only: bool = False
    revision: str = "0"


class JSONEditor(Component[JSONEditorProps]):
    props_type = JSONEditorProps
    logical_name = "JSONEditor"
    distribution = "hedron-extras"

    def __init__(
        self,
        value: Any,
        *,
        schema: Mapping[str, Any] | None = None,
        name: str = "json",
        max_chars: int = 200_000,
        read_only: bool = False,
        revision: str = "0",
        **kwargs: Any,
    ) -> None:
        if max_chars < 1 or max_chars > 200_000:
            raise ValueError("JSONEditor max_chars must be between 1 and 200000")
        text = value if isinstance(value, str) else json.dumps(value, indent=2, default=str)
        if len(text) > max_chars:
            raise ValueError(f"JSONEditor value exceeds max_chars={max_chars}")
        schema_text = json.dumps(schema) if schema is not None else None
        if schema_text is not None and len(schema_text) > max_chars:
            raise ValueError("JSONEditor schema exceeds max_chars")
        # Validate JSON parse when not read-only string of invalid content for security budgets.
        if text.strip():
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"JSONEditor value is not valid JSON: {exc.msg}") from exc
        super().__init__(
            JSONEditorProps(
                value=text,
                schema_text=schema_text,
                name=name,
                max_chars=max_chars,
                read_only=read_only,
                revision=revision,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        return html.form(
            html.textarea(
                self.props.value,
                name=self.props.name,
                readonly=self.props.read_only or None,
                rows=16,
                cols=80,
                data={"schema": self.props.schema_text, "no-eval": "true"},
                spellcheck="false",
            ),
            html.input(
                type="hidden",
                name=f"{self.props.name}__revision",
                value=self.props.revision,
            ),
            html.button("Apply", type="submit", name=f"{self.props.name}__apply", value="1"),
            html.button(
                "Cancel",
                type="submit",
                name=f"{self.props.name}__cancel",
                value="1",
                data={"hedron-cancel": "true"},
            ),
            html.button("Export", type="submit", name=f"{self.props.name}__export", value="json"),
            html.noscript(html.pre(self.props.value)),
            class_=class_names("hedron-json-editor", self.props.class_),
            id=self.props.id,
            method="post",
            data={
                **mark_data(self.props.mark),
                "hedron-workbench": "json-editor",
                "max-chars": str(self.props.max_chars),
                "revision": self.props.revision,
                "http-fallback": "textarea",
                "no-eval": "true",
            },
        )


class CodeEditorProps(ElementProps):
    value: str
    language: str = "text"
    name: str = "code"
    max_chars: int = 200_000
    read_only: bool = False
    submit_mode: Literal["full", "patch"] = "full"


class CodeEditor(Component[CodeEditorProps]):
    """CSP-safe CodeMirror-class editor host — never evaluates buffer contents."""

    props_type = CodeEditorProps
    logical_name = "CodeEditor"
    distribution = "hedron-extras"

    def __init__(
        self,
        value: str = "",
        *,
        language: str = "text",
        name: str = "code",
        max_chars: int = 200_000,
        read_only: bool = False,
        submit_mode: Literal["full", "patch"] = "full",
        **kwargs: Any,
    ) -> None:
        lang = language.lower().strip()
        if lang not in _ALLOWED_CODE_LANGUAGES:
            raise ValueError(
                f"CodeEditor language {language!r} not in allowlist: "
                f"{sorted(_ALLOWED_CODE_LANGUAGES)}"
            )
        if max_chars < 1 or max_chars > 200_000:
            raise ValueError("CodeEditor max_chars must be between 1 and 200000")
        if len(value) > max_chars:
            raise ValueError(f"CodeEditor value exceeds max_chars={max_chars}")
        super().__init__(
            CodeEditorProps(
                value=value,
                language=lang,
                name=name,
                max_chars=max_chars,
                read_only=read_only,
                submit_mode=submit_mode,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        return html.div(
            html.textarea(
                self.props.value,
                name=self.props.name,
                readonly=self.props.read_only or None,
                rows=18,
                cols=80,
                spellcheck="false",
                data={"language": self.props.language, "no-eval": "true"},
            ),
            html.noscript(
                html.pre(
                    html.code(
                        self.props.value,
                        class_=f"language-{self.props.language}",
                    )
                )
            ),
            class_=class_names("hedron-code-editor", self.props.class_),
            id=self.props.id,
            data={
                **mark_data(self.props.mark),
                "hedron-workbench": "code-editor",
                "language": self.props.language,
                "submit-mode": self.props.submit_mode,
                "no-eval": "true",
                "csp-safe": "true",
                "max-chars": str(self.props.max_chars),
                "http-fallback": "textarea",
            },
        )


class ChartWorkbenchProps(ElementProps):
    title: str = "Chart workbench"
    export_name: str = "export"
    revision: str = "0"


class ChartWorkbench(Component[ChartWorkbenchProps]):
    props_type = ChartWorkbenchProps
    logical_name = "ChartWorkbench"
    distribution = "hedron-extras"
    slots: ClassVar[dict[str, str]] = {
        "chart": "optional",
        "table": "optional",
        "explorer": "optional",
    }

    def __init__(
        self,
        *,
        title: str = "Chart workbench",
        export_name: str = "export",
        revision: str = "0",
        chart: NodeLike = None,
        table: NodeLike = None,
        explorer: NodeLike = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            ChartWorkbenchProps(title=title, export_name=export_name, revision=revision, **kwargs)
        )
        self._chart = chart
        self._table = table
        self._explorer = explorer

    def render(self) -> NodeLike:
        tabs = [
            html.section(html.h3("Chart"), self._chart, data={"tab": "chart"}),
            html.section(html.h3("Data"), self._table, data={"tab": "table"}),
            html.section(html.h3("Explore"), self._explorer, data={"tab": "explore"}),
        ]
        return html.form(
            html.h2(self.props.title),
            *tabs,
            html.button("Export CSV", type="submit", name=self.props.export_name, value="csv"),
            html.input(
                type="hidden",
                name=f"{self.props.export_name}__revision",
                value=self.props.revision,
            ),
            html.button(
                "Cancel",
                type="submit",
                name=f"{self.props.export_name}__cancel",
                value="1",
                data={"hedron-cancel": "true"},
            ),
            method="post",
            class_=class_names("hedron-chart-workbench", self.props.class_),
            id=self.props.id,
            data={
                **mark_data(self.props.mark),
                "hedron-workbench": "chart",
                "http-fallback": "sections",
                "revision": self.props.revision,
            },
        )


class CallableParam(Props):
    name: str
    label: str
    kind: Literal["str", "int", "float", "bool"] = "str"
    required: bool = True


class CallableActionFormProps(ElementProps):
    action: str
    params: list[CallableParam]
    title: str = "Run"
    form_action: SafeUrl | None = None


class CallableActionForm(Component[CallableActionFormProps]):
    """Annotation-limited callable → typed action form; never executes callables implicitly."""

    props_type = CallableActionFormProps
    logical_name = "CallableActionForm"
    distribution = "hedron-extras"

    def __init__(
        self,
        action: str,
        params: Sequence[CallableParam | Mapping[str, Any]],
        *,
        title: str = "Run",
        form_action: str | SafeUrl | None = None,
        **kwargs: Any,
    ) -> None:
        if not action or "/" in action or action.startswith("_"):
            raise ValueError("CallableActionForm action must be an explicit allowlisted action id")
        parsed = [
            p if isinstance(p, CallableParam) else CallableParam.model_validate(p) for p in params
        ]
        post_to = (
            None
            if form_action is None
            else (
                form_action
                if isinstance(form_action, SafeUrl)
                else SafeUrl.parse(form_action, purpose=UrlPurpose.FORM_ACTION)
            )
        )
        super().__init__(
            CallableActionFormProps(
                action=action,
                params=parsed,
                title=title,
                form_action=post_to,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        fields: list[NodeLike] = [html.legend(self.props.title)]
        for p in self.props.params:
            input_type = {
                "str": "text",
                "int": "number",
                "float": "number",
                "bool": "checkbox",
            }[p.kind]
            fields.append(
                html.label(
                    html.span(p.label),
                    html.input(
                        type=input_type,
                        name=p.name,
                        required=p.required or None,
                        step="any" if p.kind == "float" else None,
                    ),
                )
            )
        fields.append(html.input(type="hidden", name="hedron_action", value=self.props.action))
        fields.append(html.button(self.props.title, type="submit"))
        fields.append(
            html.button(
                "Cancel",
                type="submit",
                name="hedron_action_cancel",
                value="1",
                data={"hedron-cancel": "true"},
            )
        )
        return html.form(
            *fields,
            class_=class_names("hedron-callable-action-form", self.props.class_),
            id=self.props.id,
            method="post",
            action=self.props.form_action,
            data={
                **mark_data(self.props.mark),
                "hedron-workbench": "callable-form",
                "action": self.props.action,
                "implicit-exec": "never",
            },
        )
