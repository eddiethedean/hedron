"""Typed, serializable document AST for the bounded Markdown compiler."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, cast

_MAX_NODE_DEPTH = 256
_MAX_NODES_PER_TREE = 100_000
NODE_KINDS = frozenset(
    {
        "alert",
        "api-directive",
        "break",
        "code",
        "container",
        "dd",
        "definition-list",
        "demo-directive",
        "details",
        "divider",
        "dt",
        "emphasis",
        "footnote",
        "footnote-backref",
        "footnote-ref",
        "footnotes",
        "heading",
        "image",
        "inline-code",
        "link",
        "list",
        "list-item",
        "paragraph",
        "quote",
        "span",
        "strong",
        "tab-panel",
        "table",
        "tbody",
        "td",
        "text",
        "th",
        "thead",
        "tr",
        "tabs",
    }
)


def _is_string(value: object) -> bool:
    return isinstance(value, str)


def _is_doc_node(value: object) -> bool:
    return isinstance(value, DocNode)


@dataclass(frozen=True, slots=True)
class SourceSpan:
    """A stable, half-open source range with one-based lines and columns."""

    source: str
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    identity: str = ""

    def __post_init__(self) -> None:
        if (
            not self.source
            or min(self.start_line, self.start_column, self.end_line, self.end_column) < 1
        ):
            raise ValueError("source span must have a source and positive positions")
        if (self.end_line, self.end_column) < (self.start_line, self.start_column):
            raise ValueError("source span end precedes its start")
        expected = self.make_identity(
            self.source, self.start_line, self.start_column, self.end_line, self.end_column
        )
        if self.identity and self.identity != expected:
            raise ValueError("source span identity does not match its location")
        if not self.identity:
            object.__setattr__(self, "identity", expected)

    @staticmethod
    def make_identity(
        source: str, start_line: int, start_column: int, end_line: int, end_column: int
    ) -> str:
        value = f"{source}\0{start_line}:{start_column}-{end_line}:{end_column}"
        return "span-" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:20]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "start": [self.start_line, self.start_column],
            "end": [self.end_line, self.end_column],
            "identity": self.identity,
        }

    @classmethod
    def from_dict(cls, value: object) -> SourceSpan:
        if not isinstance(value, dict):
            raise ValueError("manifest source span must be an object")
        data = cast(dict[str, object], value)
        source, start, end, identity = (
            data.get("source"),
            data.get("start"),
            data.get("end"),
            data.get("identity"),
        )
        start_values = cast(list[object], start) if isinstance(start, list) else []
        end_values = cast(list[object], end) if isinstance(end, list) else []
        if (
            not isinstance(source, str)
            or not isinstance(start, list)
            or not isinstance(end, list)
            or len(start_values) != 2
            or len(end_values) != 2
            or not isinstance(identity, str)
        ):
            raise ValueError("manifest source span has an invalid shape")
        positions = (*start_values, *end_values)
        if any(isinstance(item, bool) or not isinstance(item, int) for item in positions):
            raise ValueError("manifest source span positions must be integers")
        start_line, start_column, end_line, end_column = cast(tuple[int, int, int, int], positions)
        return cls(source, start_line, start_column, end_line, end_column, identity)


@dataclass(frozen=True, slots=True)
class DocNode:
    kind: str
    text: str = ""
    attrs: tuple[tuple[str, str], ...] = ()
    children: tuple[DocNode, ...] = field(default_factory=tuple)
    source: str = ""
    line: int = 1
    column: int = 1
    end_line: int | None = None
    end_column: int | None = None
    span_id: str = ""

    def __post_init__(self) -> None:
        if not _is_string(self.kind) or not _is_string(self.text):
            raise ValueError("document node kind and text must be strings")
        if self.kind not in NODE_KINDS:
            raise ValueError(f"unsupported document node kind: {self.kind!r}")
        if any(not _is_string(key) or not _is_string(value) for key, value in self.attrs):
            raise ValueError("document node attrs must be a string mapping")
        if len({key for key, _ in self.attrs}) != len(self.attrs):
            raise ValueError("document node attrs must not contain duplicate keys")
        if any(not _is_doc_node(child) for child in self.children):
            raise ValueError("document node children must be document nodes")
        if min(self.line, self.column) < 1:
            raise ValueError("document node location must be positive")
        end_line = self.end_line if self.end_line is not None else self.line
        end_column = self.end_column if self.end_column is not None else self.column
        if min(end_line, end_column) < 1 or (end_line, end_column) < (self.line, self.column):
            raise ValueError("document node source range is invalid")
        if self.source:
            span = SourceSpan(
                self.source, self.line, self.column, end_line, end_column, self.span_id
            )
            if not self.span_id:
                object.__setattr__(self, "span_id", span.identity)
        elif self.span_id:
            raise ValueError("document node span identity requires a source")

    @property
    def span(self) -> SourceSpan | None:
        if not self.source:
            return None
        return SourceSpan(
            self.source,
            self.line,
            self.column,
            self.end_line or self.line,
            self.end_column or self.column,
            self.span_id,
        )

    def attr(self, name: str, default: str = "") -> str:
        return dict(self.attrs).get(name, default)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"kind": self.kind, "line": self.line}
        if self.text:
            result["text"] = self.text
        if self.attrs:
            result["attrs"] = {key: value for key, value in self.attrs}
        if self.children:
            result["children"] = [child.to_dict() for child in self.children]
        if self.span is not None:
            result["span"] = self.span.to_dict()
        return result

    @classmethod
    def from_dict(
        cls,
        value: object,
        *,
        _depth: int = 0,
        _counter: list[int] | None = None,
    ) -> DocNode:
        if _depth > _MAX_NODE_DEPTH:
            raise ValueError(f"manifest node nesting exceeds {_MAX_NODE_DEPTH} levels")
        if _counter is None:
            _counter = [0]
        _counter[0] += 1
        if _counter[0] > _MAX_NODES_PER_TREE:
            raise ValueError(f"manifest contains more than {_MAX_NODES_PER_TREE} nodes")
        if not isinstance(value, dict):
            raise ValueError("manifest node must be an object with a kind")
        data = cast(dict[str, object], value)
        kind = data.get("kind")
        if not isinstance(kind, str) or kind not in NODE_KINDS:
            raise ValueError("manifest node has an unsupported kind")
        text = data.get("text", "")
        if not isinstance(text, str):
            raise ValueError("manifest node text must be a string")
        attrs_value = data.get("attrs", {})
        if not isinstance(attrs_value, dict):
            raise ValueError("manifest node attrs must be a string mapping")
        raw_attrs = cast(dict[object, object], attrs_value)
        attrs: dict[str, str] = {}
        for key, item in raw_attrs.items():
            if not isinstance(key, str) or not isinstance(item, str):
                raise ValueError("manifest node attrs must be a string mapping")
            attrs[key] = item
        children_value = data.get("children", [])
        if not isinstance(children_value, list):
            raise ValueError("manifest node children must be an array")
        children = cast(list[object], children_value)
        span_value = data.get("span")
        if span_value is None:
            raise ValueError("manifest 3 document nodes require a source span")
        span = SourceSpan.from_dict(span_value)
        line = data.get("line", span.start_line)
        if isinstance(line, bool) or not isinstance(line, int) or line != span.start_line:
            raise ValueError("manifest node line must match its source span")
        return cls(
            kind=kind,
            text=text,
            attrs=tuple(sorted((str(key), str(item)) for key, item in attrs.items())),
            children=tuple(
                cls.from_dict(child, _depth=_depth + 1, _counter=_counter) for child in children
            ),
            source=span.source,
            line=line,
            column=span.start_column,
            end_line=span.end_line,
            end_column=span.end_column,
            span_id=span.identity,
        )
