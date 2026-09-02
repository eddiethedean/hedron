"""Small, serializable document AST used by the 0.1 compiler."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

_MAX_NODE_DEPTH = 256
_MAX_NODES_PER_TREE = 100_000


@dataclass(frozen=True, slots=True)
class DocNode:
    kind: str
    text: str = ""
    attrs: tuple[tuple[str, str], ...] = ()
    children: tuple[DocNode, ...] = field(default_factory=tuple)
    line: int = 1

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
        if not isinstance(kind, str) or not kind or len(kind) > 64:
            raise ValueError("manifest node must be an object with a kind")
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
        line = int(str(data.get("line", 1)))
        if line < 1:
            raise ValueError("manifest node line must be positive")
        return cls(
            kind=kind,
            text=str(data.get("text", "")),
            attrs=tuple(sorted((str(key), str(item)) for key, item in attrs.items())),
            children=tuple(
                cls.from_dict(child, _depth=_depth + 1, _counter=_counter) for child in children
            ),
            line=line,
        )
