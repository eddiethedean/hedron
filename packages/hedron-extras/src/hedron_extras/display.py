"""Display adapters and presentation recipes."""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

from hedron_core.builtins._base import ElementProps, class_names, mark_data
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props

_SECRETISH = re.compile(
    r"(?i)\b(password|passwd|token|secret|api[_-]?key|authorization)\b\s*[:=]\s*\S+"
)


def _redact_log_text(text: str) -> str:
    return _SECRETISH.sub(lambda m: f"{m.group(1)}=***", text)


class LogLine(Props):
    text: str
    level: str = "info"
    ts: str | None = None


class LogConsoleProps(ElementProps):
    lines: list[LogLine]
    max_lines: int = 500
    producer: str = "explicit"
    redact: bool = True


class LogConsole(Component[LogConsoleProps]):
    """Bounded job/log console — never redirects process-global stdout."""

    props_type = LogConsoleProps
    logical_name = "LogConsole"
    distribution = "hedron-extras"

    def __init__(
        self,
        lines: Sequence[LogLine | dict[str, Any]] | None = None,
        *,
        max_lines: int = 500,
        producer: str = "explicit",
        redact: bool = True,
        **kwargs: Any,
    ) -> None:
        if producer in {"stdout", "stderr", "logging-global"}:
            raise ValueError(
                "LogConsole requires an explicit producer; process-global capture is non-parity"
            )
        if max_lines < 1 or max_lines > 10_000:
            raise ValueError("LogConsole max_lines out of bounds")
        parsed = [
            line if isinstance(line, LogLine) else LogLine.model_validate(line)
            for line in (lines or [])
        ][-max_lines:]
        super().__init__(
            LogConsoleProps(
                lines=parsed,
                max_lines=max_lines,
                producer=producer,
                redact=redact,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        rows: list[NodeLike] = []
        for line in self.props.lines:
            text = _redact_log_text(line.text) if self.props.redact else line.text
            rows.append(
                html.li(
                    f"[{line.level}] {text}",
                    data={"level": line.level, "ts": line.ts},
                )
            )
        return html.div(
            html.ol(*rows),
            class_=class_names("hedron-log-console", self.props.class_),
            id=self.props.id,
            role="log",
            aria={"live": "polite"},
            data={
                **mark_data(self.props.mark),
                "hedron-display": "log",
                "producer": self.props.producer,
                "max-lines": str(self.props.max_lines),
                "redact": "1" if self.props.redact else "0",
                "backpressure": "drop-oldest",
            },
        )


class TokenSpan(Props):
    text: str
    weight: float = 0.0


class TokenWeightedTextProps(ElementProps):
    tokens: list[TokenSpan]


class TokenWeightedText(Component[TokenWeightedTextProps]):
    props_type = TokenWeightedTextProps
    logical_name = "TokenWeightedText"
    distribution = "hedron-extras"

    def __init__(self, tokens: Sequence[TokenSpan | dict[str, Any]], **kwargs: Any) -> None:
        parsed = [t if isinstance(t, TokenSpan) else TokenSpan.model_validate(t) for t in tokens]
        if len(parsed) > 20_000:
            raise ValueError("TokenWeightedText budget exceeded")
        super().__init__(TokenWeightedTextProps(tokens=parsed, **kwargs))

    def render(self) -> NodeLike:
        spans = [
            html.span(
                t.text,
                data={"weight": f"{t.weight:.4f}"},
            )
            for t in self.props.tokens
        ]
        return html.p(
            *spans,
            class_=class_names("hedron-token-weighted", self.props.class_),
            id=self.props.id,
            data={**mark_data(self.props.mark), "hedron-display": "token-weighted"},
        )


class DiagramOutputProps(ElementProps):
    source: str
    format: str = "mermaid"
    max_chars: int = 100_000


class DiagramOutput(Component[DiagramOutputProps]):
    props_type = DiagramOutputProps
    logical_name = "DiagramOutput"
    distribution = "hedron-extras"

    def __init__(
        self,
        source: str,
        *,
        format: str = "mermaid",
        max_chars: int = 100_000,
        **kwargs: Any,
    ) -> None:
        if len(source) > max_chars:
            raise ValueError("DiagramOutput source exceeds max_chars")
        if format not in {"mermaid", "graphviz", "plantuml", "text"}:
            raise ValueError(f"Unsupported diagram format: {format}")
        super().__init__(
            DiagramOutputProps(source=source, format=format, max_chars=max_chars, **kwargs)
        )

    def render(self) -> NodeLike:
        return html.div(
            html.pre(self.props.source, data={"diagram-format": self.props.format}),
            class_=class_names("hedron-diagram-output", self.props.class_),
            id=self.props.id,
            data={
                **mark_data(self.props.mark),
                "hedron-display": "diagram",
                "format": self.props.format,
                "raw-html": "never",
            },
        )
