"""Small, serializable document AST used by the 0.1 compiler."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast


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
    def from_dict(cls, value: object) -> DocNode:
        if not isinstance(value, dict):
            raise ValueError("manifest node must be an object with a kind")
        data = cast(dict[str, object], value)
        kind = data.get("kind")
        if not isinstance(kind, str):
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
        return cls(
            kind=kind,
            text=str(data.get("text", "")),
            attrs=tuple(sorted((str(key), str(item)) for key, item in attrs.items())),
            children=tuple(cls.from_dict(child) for child in children),
            line=int(str(data.get("line", 1))),
        )
