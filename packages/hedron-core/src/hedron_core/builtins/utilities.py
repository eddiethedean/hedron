"""Utility built-in components for phase 0.5."""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any, Literal

from hedron_core.component import Component
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.security import Secret


def _kids(*children: Any) -> tuple[Any, ...]:
    if (
        len(children) == 1
        and isinstance(children[0], Sequence)
        and not isinstance(children[0], (str, bytes))
    ):
        return tuple(children[0])
    return children


class MetricProps(Props):
    label: str
    value: str
    delta: str | None = None
    delta_tone: Literal["up", "down", "neutral"] = "neutral"


class Metric(Component[MetricProps]):
    props_type = MetricProps
    logical_name = "Metric"

    def __init__(
        self,
        label: str,
        value: Any,
        *,
        delta: Any = None,
        delta_tone: Literal["up", "down", "neutral"] = "neutral",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            MetricProps(
                label=label,
                value=str(value),
                delta=None if delta is None else str(delta),
                delta_tone=delta_tone,
                **kwargs,
            )
        )

    def render(self) -> Any:
        parts: list[Any] = [
            html.dt(self.props.label),
            html.dd(self.props.value, data={"metric-value": "true"}),
        ]
        if self.props.delta is not None:
            parts.append(
                html.dd(
                    self.props.delta,
                    data={"metric-delta": self.props.delta_tone},
                    aria={"label": f"change {self.props.delta}"},
                )
            )
        return html.dl(*parts, class_="hedron-metric", role="group")


class CodeViewerProps(Props):
    code: str
    language: str | None = None
    max_chars: int = 100_000


class CodeViewer(Component[CodeViewerProps]):
    props_type = CodeViewerProps
    logical_name = "CodeViewer"

    def __init__(
        self,
        code: str,
        *,
        language: str | None = None,
        max_chars: int = 100_000,
        **kwargs: Any,
    ) -> None:
        clipped = code if len(code) <= max_chars else code[:max_chars] + "\n… [truncated]"
        super().__init__(
            CodeViewerProps(code=clipped, language=language, max_chars=max_chars, **kwargs)
        )

    def render(self) -> Any:
        attrs: dict[str, Any] = {}
        if self.props.language:
            attrs["class_"] = f"language-{self.props.language}"
            attrs["data"] = {"language": self.props.language}
        return html.pre(html.code(self.props.code, **attrs), class_="hedron-code-viewer")


def _redact_json(value: Any, *, depth: int = 0) -> Any:
    if depth > 20:
        return "[max-depth]"
    if isinstance(value, Secret):
        return "***"
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            key = str(k)
            if "secret" in key.lower() or "password" in key.lower() or "token" in key.lower():
                out[key] = "***"
            else:
                out[key] = _redact_json(v, depth=depth + 1)
        return out
    if isinstance(value, list):
        return [_redact_json(v, depth=depth + 1) for v in value[:500]]
    return value


class JSONViewerProps(Props):
    text: str
    max_chars: int = 100_000


class JSONViewer(Component[JSONViewerProps]):
    props_type = JSONViewerProps
    logical_name = "JSONViewer"

    def __init__(self, value: Any, *, max_chars: int = 100_000, **kwargs: Any) -> None:
        redacted = _redact_json(value)
        text = json.dumps(redacted, indent=2, default=str)
        if len(text) > max_chars:
            text = text[:max_chars] + "\n… [truncated]"
        super().__init__(JSONViewerProps(text=text, max_chars=max_chars, **kwargs))

    def render(self) -> Any:
        return html.pre(
            html.code(self.props.text, class_="language-json"),
            class_="hedron-json-viewer",
        )


class ProgressProps(Props):
    value: float
    maximum: float = 100
    label: str | None = None


class Progress(Component[ProgressProps]):
    props_type = ProgressProps
    logical_name = "Progress"

    def __init__(
        self,
        value: float,
        *,
        maximum: float = 100,
        label: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(ProgressProps(value=value, maximum=maximum, label=label, **kwargs))

    def render(self) -> Any:
        attrs: dict[str, Any] = {
            "value": str(self.props.value),
            "max": str(self.props.maximum),
        }
        if self.props.label:
            attrs["aria-label"] = self.props.label
        return html.progress(**attrs)


class StatusProps(Props):
    message: str
    tone: Literal["info", "success", "warning", "danger"] = "info"
    live: bool = True


class Status(Component[StatusProps]):
    props_type = StatusProps
    logical_name = "Status"

    def __init__(
        self,
        message: str,
        *,
        tone: Literal["info", "success", "warning", "danger"] = "info",
        live: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(StatusProps(message=message, tone=tone, live=live, **kwargs))

    def render(self) -> Any:
        attrs: dict[str, Any] = {
            "class_": f"hedron-status hedron-status-{self.props.tone}",
            "role": "status",
        }
        if self.props.live:
            attrs["aria"] = {"live": "polite"}
        return html.div(self.props.message, **attrs)


class ToastProps(Props):
    message: str
    tone: Literal["info", "success", "warning", "danger"] = "info"


class Toast(Component[ToastProps]):
    props_type = ToastProps
    logical_name = "Toast"

    def __init__(
        self,
        message: str,
        *,
        tone: Literal["info", "success", "warning", "danger"] = "info",
        **kwargs: Any,
    ) -> None:
        super().__init__(ToastProps(message=message, tone=tone, **kwargs))

    def render(self) -> Any:
        return html.div(
            self.props.message,
            class_=f"hedron-toast hedron-toast-{self.props.tone}",
            role="status",
            aria={"live": "polite"},
        )


class ExpanderProps(Props):
    title: str
    open: bool = False


class Expander(Component[ExpanderProps]):
    props_type = ExpanderProps
    logical_name = "Expander"
    slots = {"body": "optional"}

    def __init__(self, title: str, *children: Any, open: bool = False, **kwargs: Any) -> None:
        super().__init__(ExpanderProps(title=title, open=open, **kwargs))
        self._body = _kids(*children)

    def render(self) -> Any:
        attrs: dict[str, Any] = {}
        if self.props.open:
            attrs["open"] = True
        body = self._slot_values.get("body", self._body)
        if not isinstance(body, tuple):
            body = (body,)
        return html.details(html.summary(self.props.title), *body, **attrs)


class TabsProps(Props):
    active: str | None = None


class Tabs(Component[TabsProps]):
    props_type = TabsProps
    logical_name = "Tabs"

    def __init__(
        self,
        *panels: tuple[str, Any],
        active: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(TabsProps(active=active, **kwargs))
        self._panels = panels

    def render(self) -> Any:
        if not self._panels:
            return html.div(class_="hedron-tabs")
        active = self.props.active or self._panels[0][0]
        tablist = []
        panels = []
        for idx, (name, content) in enumerate(self._panels):
            tab_id = f"tab-{idx}"
            panel_id = f"panel-{idx}"
            selected = name == active
            tablist.append(
                html.button(
                    name,
                    type="button",
                    role="tab",
                    id=tab_id,
                    aria={
                        "selected": "true" if selected else "false",
                        "controls": panel_id,
                    },
                    tabindex="0" if selected else "-1",
                )
            )
            panels.append(
                html.div(
                    content,
                    role="tabpanel",
                    id=panel_id,
                    aria={"labelledby": tab_id},
                    hidden=None if selected else True,
                )
            )
        return html.div(
            html.div(*tablist, role="tablist", class_="hedron-tablist"),
            *panels,
            class_="hedron-tabs",
        )


class SidebarProps(Props):
    label: str = "Sidebar"


class Sidebar(Component[SidebarProps]):
    props_type = SidebarProps
    logical_name = "Sidebar"
    slots = {"body": "optional"}

    def __init__(self, *children: Any, label: str = "Sidebar", **kwargs: Any) -> None:
        super().__init__(SidebarProps(label=label, **kwargs))
        self._body = _kids(*children)

    def render(self) -> Any:
        body = self._slot_values.get("body", self._body)
        if not isinstance(body, tuple):
            body = (body,)
        return html.aside(*body, class_="hedron-sidebar", aria={"label": self.props.label})
