"""HDN render program runtime."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from hedron_core.codes import (
    HED_HDN_FORMAT,
    HED_HDN_TRUSTED,
    HED_HDN_TYPE,
    HED_HDN_UNKNOWN_COMPONENT,
)
from hedron_core.diagnostics import error
from hedron_core.hdn.expr import eval_expr
from hedron_core.html import html
from hedron_core.security import TrustedHtml

__all__ = ["Op", "RenderProgram", "load_hdn_program", "run_program"]

HDN_FORMAT_VERSION = 1


@dataclass(frozen=True, slots=True)
class Op:
    kind: str
    data: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RenderProgram:
    format_version: int
    ops: tuple[Op, ...]
    source_map: tuple[Mapping[str, Any], ...] = ()
    dependencies: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "format_version": self.format_version,
            "ops": [{"kind": op.kind, "data": dict(op.data)} for op in self.ops],
            "source_map": list(self.source_map),
            "dependencies": list(self.dependencies),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> RenderProgram:
        format_version = int(data["format_version"])
        if format_version != HDN_FORMAT_VERSION:
            raise error(
                HED_HDN_FORMAT,
                title="Unsupported HDN program format",
                explanation=(
                    f"HDN program format_version {format_version} is not supported "
                    f"(expected {HDN_FORMAT_VERSION})."
                ),
                remediation="Rebuild with a matching Hedron release.",
            )
        ops = tuple(
            Op(kind=str(item["kind"]), data=dict(item.get("data") or {}))
            for item in data.get("ops", ())
        )
        return cls(
            format_version=format_version,
            ops=ops,
            source_map=tuple(dict(item) for item in data.get("source_map", ())),
            dependencies=tuple(str(x) for x in data.get("dependencies", ())),
        )


def load_hdn_program(path: Path | str) -> RenderProgram:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return RenderProgram.from_dict(payload)


def run_program(
    program: RenderProgram,
    scope: Mapping[str, Any],
    *,
    components: Mapping[str, Any] | None = None,
) -> Any:
    """Execute a compiled render program into NodeLike structures."""
    comps = dict(components or {})
    return _run_ops(list(program.ops), dict(scope), comps)


def _run_ops(ops: list[Op], scope: dict[str, Any], components: dict[str, Any]) -> list[Any]:
    out: list[Any] = []
    i = 0
    while i < len(ops):
        op = ops[i]
        kind = op.kind
        if kind == "text":
            out.append(op.data["value"])
            i += 1
        elif kind == "expr":
            value = eval_expr(str(op.data["source"]), scope)
            out.append("" if value is None else value)
            i += 1
        elif kind == "raw_html":
            value = eval_expr(str(op.data["source"]), scope)
            if not isinstance(value, TrustedHtml):
                raise error(
                    HED_HDN_TRUSTED,
                    title="TrustedHtml required",
                    explanation="{@html} only accepts TrustedHtml values.",
                    remediation="Wrap reviewed HTML with TrustedHtml.reviewed(...).",
                )
            out.append(html.raw(value))
            i += 1
        elif kind == "element":
            tag = str(op.data["tag"])
            child_count = int(op.data["child_count"])
            attr_specs: Sequence[Mapping[str, Any]] = op.data.get("attrs", ())
            i += 1
            children = _run_ops(ops[i : i + child_count], scope, components)
            i += child_count
            attrs: dict[str, Any] = {}
            for spec in attr_specs:
                name = str(spec["name"])
                if spec.get("kind") == "expr":
                    attrs[name] = eval_expr(str(spec["source"]), scope)
                else:
                    attrs[name] = spec.get("value")
            node = _make_element(tag, attrs, children, components)
            out.append(node)
        elif kind == "fragment":
            child_count = int(op.data["child_count"])
            i += 1
            children = _run_ops(ops[i : i + child_count], scope, components)
            i += child_count
            out.extend(children)
        elif kind == "if":
            then_count = int(op.data["then_count"])
            else_count = int(op.data["else_count"])
            cond = eval_expr(str(op.data["condition"]), scope)
            i += 1
            then_ops = ops[i : i + then_count]
            i += then_count
            else_ops = ops[i : i + else_count]
            i += else_count
            chosen = then_ops if cond else else_ops
            out.extend(_run_ops(chosen, scope, components))
        elif kind == "for":
            body_count = int(op.data["body_count"])
            item_name = str(op.data["item"])
            iterable = eval_expr(str(op.data["iterable"]), scope)
            i += 1
            body_ops = ops[i : i + body_count]
            i += body_count
            try:
                iterator = iter(iterable)
            except TypeError as exc:
                raise error(
                    HED_HDN_TYPE,
                    title="For-loop iterable required",
                    explanation=f"{{#for}} expected an iterable, got {type(iterable).__name__}.",
                    remediation="Pass a list, tuple, or other iterable in scope.",
                ) from exc
            for item in iterator:
                child_scope = dict(scope)
                child_scope[item_name] = item
                out.extend(_run_ops(body_ops, child_scope, components))
        else:
            raise error(
                HED_HDN_UNKNOWN_COMPONENT,
                title="Unknown render opcode",
                explanation=f"Opcode {kind!r} is not supported.",
                remediation="Recompile the HDN template.",
            )
    return out


def _make_element(
    tag: str,
    attrs: dict[str, Any],
    children: list[Any],
    components: dict[str, Any],
) -> Any:
    html_attrs = _html_attrs(attrs)
    if tag[:1].isupper():
        cls = components.get(tag)
        if cls is None:
            raise error(
                HED_HDN_UNKNOWN_COMPONENT,
                title="Unknown HDN component",
                explanation=f"Component tag <{tag}> is not registered in the render scope.",
                remediation="Pass the component class in the components mapping.",
            )
        props = dict(attrs)
        if "class" in props:
            props["class_"] = props.pop("class")
        if "for" in props:
            props["for_"] = props.pop("for")
        inst = cls(**props)
        if children:
            inst = inst.children(*children)
        return inst
    from hedron_core.html import _HtmlTag

    return _HtmlTag(tag)(*children, **html_attrs)


def _html_attrs(attrs: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in attrs.items():
        if key == "class":
            out["class_"] = value
        elif key == "for":
            out["for_"] = value
        else:
            out[key] = value
    return out
