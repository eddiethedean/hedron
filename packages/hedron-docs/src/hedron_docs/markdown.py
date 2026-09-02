"""Token-based Markdown-to-document-AST adapter.

The parser never renders or reparses HTML. CommonMark tokens and explicitly recognized extensions
are lowered directly into the closed :class:`DocNode` vocabulary with stable source spans.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdit_py_plugins.attrs import attrs_plugin
from mdit_py_plugins.deflist import deflist_plugin
from mdit_py_plugins.footnote import footnote_plugin

from .ast import DocNode
from .errors import source_error

_ADMONITION = re.compile(
    r'^(?P<marker>!!!|\?\?\?\+?)\s+(?P<type>[A-Za-z][\w-]*)(?:\s+["\'](?P<title>.*?)["\'])?\s*$'
)
_TAB = re.compile(r'^===\s+["\'](?P<label>.+?)["\']\s*$')
_DIRECTIVE = re.compile(r"^:::\s*(?P<target>.*?)\s*$")
_API_TARGET = re.compile(r"^[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*$", re.UNICODE)
_DEMO_TARGET = re.compile(r"^[a-z][a-z0-9]*(?:[-_.][a-z0-9]+)*$")
_EXPLICIT_HEADING_ID = re.compile(r"\s*\{#(?P<id>[A-Za-z][\w:.-]*)\}\s*$", re.UNICODE)
_ATTRIBUTE_LIST = re.compile(r"\{\s*(?:[#.][\w:-]+)(?:\s+[#.][\w:-]+)*\s*\}")
_EXTENSION_PREFIX = ("!!!", "???", "???+", "===", ":::")
_FENCE_START = re.compile(r"^ {0,3}(?P<marker>`{3,}|~{3,})")

_OPEN_KINDS = {
    "heading_open": "heading",
    "paragraph_open": "paragraph",
    "bullet_list_open": "list",
    "ordered_list_open": "list",
    "list_item_open": "list-item",
    "blockquote_open": "quote",
    "table_open": "table",
    "thead_open": "thead",
    "tbody_open": "tbody",
    "tr_open": "tr",
    "th_open": "th",
    "td_open": "td",
    "dl_open": "definition-list",
    "dt_open": "dt",
    "dd_open": "dd",
    "footnote_block_open": "footnotes",
    "footnote_open": "footnote",
}
_INLINE_OPEN_KINDS = {"em_open": "emphasis", "strong_open": "strong", "link_open": "link"}


@dataclass(frozen=True, slots=True)
class ParserLimits:
    max_source_bytes: int = 2_000_000
    max_nodes: int = 10_000
    max_depth: int = 64
    max_table_cells: int = 10_000
    max_code_blocks: int = 200
    max_code_block_bytes: int = 256_000
    max_directives: int = 100

    def __post_init__(self) -> None:
        values = (
            self.max_source_bytes,
            self.max_nodes,
            self.max_depth,
            self.max_table_cells,
            self.max_code_blocks,
            self.max_code_block_bytes,
            self.max_directives,
        )
        if any(type(value) is not int or value < 1 for value in values):
            raise ValueError("parser limits must be positive integers")


@dataclass(slots=True)
class _Builder:
    token: Token
    kind: str
    children: list[DocNode] = field(default_factory=list[DocNode])


@dataclass(slots=True)
class _InlineBuilder:
    token: Token
    kind: str
    start: int
    children: list[DocNode] = field(default_factory=list[DocNode])


class _Parser:
    def __init__(
        self, source: str, source_path: Path, source_name: str, limits: ParserLimits
    ) -> None:
        self.source = source
        self.source_path = source_path
        self.source_name = source_name
        self.limits = limits
        self.source_lines = source.splitlines()
        if source.endswith(("\n", "\r")):
            self.source_lines.append("")
        self.heading_counts: dict[str, int] = {}
        self.directive_count = 0
        self.code_count = 0
        self.markdown = (
            MarkdownIt("commonmark", {"html": True})
            .enable("table")
            .use(footnote_plugin)
            .use(deflist_plugin)
            .use(attrs_plugin)
        )
        # Preserve URL-bearing syntax as a typed node; the manifest compiler owns the stricter
        # SafeUrl policy and must diagnose it rather than silently turning it back into text.
        self.markdown.validateLink = lambda url: bool(url) or True
        self.markdown.options["maxNesting"] = limits.max_depth + 8

    def parse(self) -> tuple[DocNode, ...]:
        encoded_size = len(self.source.encode("utf-8"))
        if encoded_size > self.limits.max_source_bytes:
            raise source_error(
                "HED-DOCS-0102",
                f"document exceeds source limit ({self.limits.max_source_bytes} bytes)",
                self.source_path,
                line=1,
                column=1,
            )
        nodes = tuple(self._parse_extensions(self.source, base_line=0, column_offset=0, depth=0))
        self._check_tree_budgets(nodes)
        return nodes

    def _parse_extensions(
        self, text: str, *, base_line: int, column_offset: int, depth: int
    ) -> list[DocNode]:
        if depth > self.limits.max_depth:
            raise self._error(
                "HED-DOCS-0103",
                f"document exceeds nesting limit ({self.limits.max_depth})",
                base_line,
                column_offset + 1,
            )
        lines = text.splitlines(keepends=True)
        output: list[DocNode] = []
        index = 0
        ordinary_start = 0
        active_fence = ""

        def flush(end: int) -> None:
            nonlocal ordinary_start
            if end > ordinary_start:
                chunk = "".join(lines[ordinary_start:end])
                if chunk.strip():
                    output.extend(
                        self._parse_commonmark(
                            chunk,
                            base_line=base_line + ordinary_start,
                            column_offset=column_offset,
                        )
                    )
            ordinary_start = end

        while index < len(lines):
            line_text = lines[index].rstrip("\r\n")
            fence_match = _FENCE_START.match(line_text)
            if active_fence:
                if (
                    fence_match
                    and fence_match.group("marker")[0] == active_fence[0]
                    and len(fence_match.group("marker")) >= len(active_fence)
                ):
                    active_fence = ""
                index += 1
                continue
            if fence_match:
                active_fence = fence_match.group("marker")
                index += 1
                continue
            tab_match = _TAB.fullmatch(line_text)
            admonition_match = _ADMONITION.fullmatch(line_text)
            directive_match = _DIRECTIVE.fullmatch(line_text)
            if not (tab_match or admonition_match or directive_match):
                if line_text.startswith(_EXTENSION_PREFIX):
                    raise self._error(
                        "HED-DOCS-0108",
                        f"malformed Markdown extension marker: {line_text!r}",
                        base_line + index,
                        column_offset + 1,
                    )
                index += 1
                continue
            flush(index)
            if tab_match:
                node, index = self._parse_tabs(
                    lines,
                    index,
                    base_line=base_line,
                    column_offset=column_offset,
                    depth=depth,
                )
            elif admonition_match:
                node, index = self._parse_admonition(
                    lines,
                    index,
                    admonition_match,
                    base_line=base_line,
                    column_offset=column_offset,
                    depth=depth,
                )
            else:
                node, index = self._parse_directive(
                    lines,
                    index,
                    cast(re.Match[str], directive_match),
                    base_line=base_line,
                    column_offset=column_offset,
                )
            output.append(node)
            ordinary_start = index
        flush(len(lines))
        return output

    def _indented_body(self, lines: list[str], marker_index: int) -> tuple[str, int, int, int]:
        index = marker_index + 1
        body: list[str] = []
        first_content = index
        while index < len(lines):
            raw = lines[index]
            bare = raw.rstrip("\r\n")
            if not bare.strip():
                body.append("\n" if raw.endswith("\n") else "")
                index += 1
                continue
            if raw.startswith("    "):
                if not any(item.strip() for item in body):
                    first_content = index
                body.append(raw[4:])
                index += 1
                continue
            break
        while body and not body[-1].strip():
            body.pop()
        return "".join(body), index, first_content, max(marker_index, index - 1)

    def _parse_tabs(
        self,
        lines: list[str],
        start: int,
        *,
        base_line: int,
        column_offset: int,
        depth: int,
    ) -> tuple[DocNode, int]:
        panels: list[DocNode] = []
        index = start
        last_line = start
        while index < len(lines):
            match = _TAB.fullmatch(lines[index].rstrip("\r\n"))
            if match is None:
                break
            label = match.group("label").strip()
            if not label:
                raise self._error(
                    "HED-DOCS-0108", "tab label must not be empty", base_line + index, 1
                )
            body, next_index, first_content, last_line = self._indented_body(lines, index)
            if not body.strip():
                raise self._error(
                    "HED-DOCS-0108",
                    f"tab {label!r} requires an indented body",
                    base_line + index,
                    column_offset + 1,
                )
            children = tuple(
                self._parse_extensions(
                    body,
                    base_line=base_line + first_content,
                    column_offset=column_offset + 4,
                    depth=depth + 1,
                )
            )
            panels.append(
                self._node(
                    "tab-panel",
                    base_line + index,
                    base_line + last_line,
                    column_offset=column_offset,
                    text=label,
                    children=children,
                )
            )
            index = next_index
        return (
            self._node(
                "tabs",
                base_line + start,
                base_line + last_line,
                column_offset=column_offset,
                children=tuple(panels),
            ),
            index,
        )

    def _parse_admonition(
        self,
        lines: list[str],
        index: int,
        match: re.Match[str],
        *,
        base_line: int,
        column_offset: int,
        depth: int,
    ) -> tuple[DocNode, int]:
        body, next_index, first_content, last_line = self._indented_body(lines, index)
        if not body.strip():
            raise self._error(
                "HED-DOCS-0108",
                "admonition requires an indented body",
                base_line + index,
                column_offset + 1,
            )
        source_type = match.group("type").casefold()
        tone = {
            "note": "info",
            "tip": "info",
            "info": "info",
            "success": "success",
            "warning": "warning",
            "caution": "warning",
            "danger": "danger",
            "error": "danger",
        }.get(source_type, "info")
        marker = match.group("marker")
        kind = "alert" if marker == "!!!" else "details"
        title = (match.group("title") or source_type.replace("-", " ").title()).strip()
        children = tuple(
            self._parse_extensions(
                body,
                base_line=base_line + first_content,
                column_offset=column_offset + 4,
                depth=depth + 1,
            )
        )
        attrs = {"tone": tone, "title": title, "type": source_type}
        if kind == "details":
            attrs["open"] = "true" if marker == "???+" else "false"
        return (
            self._node(
                kind,
                base_line + index,
                base_line + last_line,
                column_offset=column_offset,
                text=" ".join(self._plain_text(child) for child in children).strip(),
                attrs=attrs,
                children=children,
            ),
            next_index,
        )

    def _parse_directive(
        self,
        lines: list[str],
        index: int,
        match: re.Match[str],
        *,
        base_line: int,
        column_offset: int,
    ) -> tuple[DocNode, int]:
        target = match.group("target").strip()
        if not target:
            raise self._error(
                "HED-DOCS-0108",
                "directive requires an API symbol or 'demo <identifier>'",
                base_line + index,
                column_offset + 1,
            )
        body, next_index, _, last_line = self._indented_body(lines, index)
        self.directive_count += 1
        if self.directive_count > self.limits.max_directives:
            raise self._error(
                "HED-DOCS-0106",
                f"document exceeds directive limit ({self.limits.max_directives})",
                base_line + index,
                column_offset + 1,
            )
        directive_kind = "api-directive"
        attrs: dict[str, str]
        if target.startswith("demo ") or target.startswith("hedron-demo "):
            identifier = target.split(maxsplit=1)[1].strip()
            if not _DEMO_TARGET.fullmatch(identifier):
                raise self._error(
                    "HED-DOCS-0108",
                    f"unsafe demo identifier: {identifier!r}",
                    base_line + index,
                    column_offset + 1,
                )
            directive_kind = "demo-directive"
            attrs = {"id": identifier}
        else:
            if not _API_TARGET.fullmatch(target) or any(
                part.startswith("_") for part in target.split(".")
            ):
                raise self._error(
                    "HED-DOCS-0108",
                    f"unsafe API directive target: {target!r}",
                    base_line + index,
                    column_offset + 1,
                )
            attrs = {"target": target}
        if body.strip():
            attrs["options"] = "\n".join(line.rstrip() for line in body.splitlines()).strip()
        return (
            self._node(
                directive_kind,
                base_line + index,
                base_line + last_line,
                column_offset=column_offset,
                attrs=attrs,
            ),
            next_index,
        )

    def _parse_commonmark(self, text: str, *, base_line: int, column_offset: int) -> list[DocNode]:
        tokens = self.markdown.parse(text)
        output: list[DocNode] = []
        stack: list[_Builder] = []

        def append(node: DocNode) -> None:
            (stack[-1].children if stack else output).append(node)

        for token in tokens:
            if token.type in {"html_block", "html_inline"}:
                line = base_line + (token.map[0] if token.map else 0)
                raise self._error(
                    "HED-DOCS-0100",
                    "raw HTML is not supported; use Markdown components",
                    line,
                    column_offset + 1,
                )
            if token.type in _OPEN_KINDS:
                stack.append(_Builder(token, _OPEN_KINDS[token.type]))
                continue
            if token.type.endswith("_close"):
                expected = token.type.removesuffix("_close") + "_open"
                if not stack or stack[-1].token.type != expected:
                    raise self._unsupported(token, base_line, column_offset)
                builder = stack.pop()
                append(self._build_block(builder, base_line, column_offset))
                continue
            if token.type == "inline":
                inline_nodes = self._parse_inline(token, base_line, column_offset)
                target = stack[-1].children if stack else output
                target.extend(inline_nodes)
                continue
            if token.type in {"fence", "code_block"}:
                self.code_count += 1
                content_bytes = len(token.content.encode("utf-8"))
                if (
                    self.code_count > self.limits.max_code_blocks
                    or content_bytes > self.limits.max_code_block_bytes
                ):
                    line = base_line + (token.map[0] if token.map else 0)
                    raise self._error(
                        "HED-DOCS-0105",
                        "document exceeds code block count or byte limit "
                        f"({self.limits.max_code_blocks} blocks, "
                        f"{self.limits.max_code_block_bytes} bytes each)",
                        line,
                        column_offset + 1,
                    )
                language = token.info.strip().split(maxsplit=1)[0] if token.info.strip() else ""
                append(
                    self._node_from_token(
                        "code",
                        token,
                        base_line,
                        column_offset,
                        text=token.content,
                        attrs={"language": language},
                    )
                )
                continue
            if token.type == "hr":
                append(self._node_from_token("divider", token, base_line, column_offset))
                continue
            if token.type == "footnote_anchor":
                label = str(token.meta.get("label", token.meta.get("id", "")))
                anchor = (
                    stack[-1].children[-1]
                    if stack and stack[-1].children
                    else self._node_from_token("footnote-backref", token, base_line, column_offset)
                )
                append(
                    DocNode(
                        "footnote-backref",
                        attrs=(("label", label),),
                        source=anchor.source,
                        line=anchor.end_line or anchor.line,
                        column=anchor.end_column or anchor.column,
                        end_line=anchor.end_line,
                        end_column=anchor.end_column,
                    )
                )
                continue
            raise self._unsupported(token, base_line, column_offset)
        if stack:
            raise self._unsupported(stack[-1].token, base_line, column_offset)
        return output

    def _build_block(self, builder: _Builder, base_line: int, column_offset: int) -> DocNode:
        token = builder.token
        attrs: dict[str, str] = {}
        children = tuple(builder.children)
        text = "".join(self._plain_text(child) for child in children)
        if builder.kind == "heading":
            attrs["level"] = token.tag.removeprefix("h") or "2"
            text, children, explicit_id = self._heading_parts(text, children)
            base_id = explicit_id or slugify(text)
            self.heading_counts[base_id] = self.heading_counts.get(base_id, 0) + 1
            count = self.heading_counts[base_id]
            attrs["id"] = base_id if count == 1 else f"{base_id}-{count}"
        elif builder.kind == "list":
            attrs["ordered"] = "true" if token.type == "ordered_list_open" else "false"
            if token.type == "ordered_list_open" and token.attrGet("start"):
                attrs["start"] = str(token.attrGet("start"))
        elif builder.kind == "footnote":
            attrs["label"] = str(token.meta.get("label", token.meta.get("id", "")))
        return self._node_from_token(
            builder.kind,
            token,
            base_line,
            column_offset,
            text=text,
            attrs=attrs,
            children=children,
        )

    def _parse_inline(self, token: Token, base_line: int, column_offset: int) -> list[DocNode]:
        children = token.children or []
        output: list[DocNode] = []
        stack: list[_InlineBuilder] = []
        locator = _InlineLocator(self, token, base_line, column_offset)

        def append(node: DocNode) -> None:
            (stack[-1].children if stack else output).append(node)

        for child in children:
            if child.type == "html_inline":
                line, column, _, _ = locator.range_for(locator.cursor, locator.cursor + 1)
                raise self._error(
                    "HED-DOCS-0100",
                    "raw HTML is not supported; use Markdown components",
                    line - 1,
                    column,
                )
            if child.type in _INLINE_OPEN_KINDS:
                allowed: set[str] = {"href", "title"} if child.type == "link_open" else set()
                if set(child.attrs) - allowed:
                    line, column, _, _ = locator.range_for(locator.cursor, locator.cursor + 1)
                    raise source_error(
                        "HED-DOCS-0107",
                        "inline attribute lists are not supported by the 0.2 typed node contract",
                        self.source_path,
                        line=line,
                        column=column,
                    )
                marker = "[" if child.type == "link_open" else child.markup
                start = locator.find(marker)
                stack.append(_InlineBuilder(child, _INLINE_OPEN_KINDS[child.type], start))
                continue
            if child.type in {"em_close", "strong_close", "link_close"}:
                expected = child.type.removesuffix("_close") + "_open"
                if not stack or stack[-1].token.type != expected:
                    raise self._unsupported(child, base_line, column_offset)
                builder = stack.pop()
                marker = ")" if child.type == "link_close" else child.markup
                end_start = locator.find(marker)
                end = end_start + len(marker)
                attrs: dict[str, str] = {}
                if builder.kind == "link":
                    href = builder.token.attrGet("href")
                    if href is not None:
                        attrs["href"] = str(href)
                    title = builder.token.attrGet("title")
                    if title is not None:
                        attrs["title"] = str(title)
                node = locator.node(
                    builder.kind,
                    builder.start,
                    end,
                    text="".join(self._plain_text(item) for item in builder.children),
                    attrs=attrs,
                    children=tuple(builder.children),
                )
                append(node)
                continue
            if child.type == "text":
                if _ATTRIBUTE_LIST.fullmatch(
                    child.content.strip()
                ) and not _EXPLICIT_HEADING_ID.search(token.content):
                    line, column, _, _ = locator.range_for(locator.cursor, locator.cursor + 1)
                    raise source_error(
                        "HED-DOCS-0107",
                        "standalone attribute lists are not supported",
                        self.source_path,
                        line=line,
                        column=column,
                    )
                start = locator.find(child.content)
                append(locator.node("text", start, start + len(child.content), text=child.content))
                continue
            if child.type == "code_inline":
                marker = child.markup or "`"
                start = locator.find(marker)
                end = locator.find(marker, start=start + len(marker)) + len(marker)
                append(locator.node("inline-code", start, end, text=child.content))
                continue
            if child.type in {"softbreak", "hardbreak"}:
                start = locator.find("\n")
                if child.type == "softbreak":
                    append(locator.node("text", start, start + 1, text="\n"))
                else:
                    append(locator.node("break", start, start + 1))
                continue
            if child.type == "image":
                if set(child.attrs) - {"src", "alt", "title"}:
                    line, column, _, _ = locator.range_for(locator.cursor, locator.cursor + 1)
                    raise source_error(
                        "HED-DOCS-0107",
                        "image attribute lists are not supported by the 0.2 typed node contract",
                        self.source_path,
                        line=line,
                        column=column,
                    )
                start = locator.find("![")
                end_start = locator.find(")", start=start + 2)
                attrs: dict[str, str] = {
                    "src": str(child.attrGet("src") or ""),
                    "alt": child.content,
                }
                title = child.attrGet("title")
                if title is not None:
                    attrs["title"] = str(title)
                append(locator.node("image", start, end_start + 1, attrs=attrs))
                continue
            if child.type == "footnote_ref":
                label = str(child.meta.get("label", child.meta.get("id", "")))
                marker = f"[^{label}]"
                start = locator.find(marker)
                append(
                    locator.node(
                        "footnote-ref",
                        start,
                        start + len(marker),
                        text=label,
                        attrs={"label": label},
                    )
                )
                continue
            raise self._unsupported(child, base_line, column_offset)
        if stack:
            raise self._unsupported(stack[-1].token, base_line, column_offset)
        return output

    def _heading_parts(
        self, text: str, children: tuple[DocNode, ...]
    ) -> tuple[str, tuple[DocNode, ...], str | None]:
        match = _EXPLICIT_HEADING_ID.search(text)
        if match is None:
            return text, children, None
        trim = len(match.group(0))
        remaining = trim
        mutable = list(children)
        while remaining and mutable:
            last = mutable[-1]
            if last.kind != "text":
                break
            if len(last.text) <= remaining:
                remaining -= len(last.text)
                mutable.pop()
            else:
                mutable[-1] = DocNode(
                    kind="text",
                    text=last.text[:-remaining],
                    source=last.source,
                    line=last.line,
                    column=last.column,
                    end_line=last.end_line,
                    end_column=max(last.column, (last.end_column or last.column) - remaining),
                )
                remaining = 0
        return text[:-trim], tuple(mutable), match.group("id")

    def _check_tree_budgets(self, nodes: tuple[DocNode, ...]) -> None:
        count = 0
        table_cells = 0
        pending = [(node, 1) for node in reversed(nodes)]
        while pending:
            node, depth = pending.pop()
            count += 1
            if count > self.limits.max_nodes:
                raise source_error(
                    "HED-DOCS-0101",
                    f"document exceeds node limit ({self.limits.max_nodes})",
                    self.source_path,
                    line=node.line,
                    column=node.column,
                )
            if depth > self.limits.max_depth:
                raise source_error(
                    "HED-DOCS-0103",
                    f"document exceeds nesting limit ({self.limits.max_depth})",
                    self.source_path,
                    line=node.line,
                    column=node.column,
                )
            if node.kind in {"th", "td"}:
                table_cells += 1
                if table_cells > self.limits.max_table_cells:
                    raise source_error(
                        "HED-DOCS-0104",
                        f"document exceeds table cell limit ({self.limits.max_table_cells})",
                        self.source_path,
                        line=node.line,
                        column=node.column,
                    )
            pending.extend((child, depth + 1) for child in reversed(node.children))

    def _node_from_token(
        self,
        kind: str,
        token: Token,
        base_line: int,
        column_offset: int,
        *,
        text: str = "",
        attrs: dict[str, str] | None = None,
        children: tuple[DocNode, ...] = (),
    ) -> DocNode:
        if token.map:
            start = base_line + token.map[0]
            end = base_line + max(token.map[0], token.map[1] - 1)
        elif children:
            start = children[0].line - 1
            end = (children[-1].end_line or children[-1].line) - 1
        else:
            start = base_line
            end = base_line
        return self._node(
            kind,
            start,
            end,
            column_offset=column_offset,
            text=text,
            attrs=attrs,
            children=children,
        )

    def _node(
        self,
        kind: str,
        start_line_zero: int,
        end_line_zero: int,
        *,
        column_offset: int,
        text: str = "",
        attrs: dict[str, str] | None = None,
        children: tuple[DocNode, ...] = (),
    ) -> DocNode:
        start_text = self.source_line(start_line_zero)
        start_column = (
            column_offset
            + len(start_text[column_offset:])
            - len(start_text[column_offset:].lstrip())
            + 1
        )
        end_column = len(self.source_line(end_line_zero)) + 1
        if end_line_zero == start_line_zero:
            end_column = max(start_column, end_column)
        return DocNode(
            kind=kind,
            text=text,
            attrs=tuple(sorted((attrs or {}).items())),
            children=children,
            source=self.source_name,
            line=start_line_zero + 1,
            column=start_column,
            end_line=end_line_zero + 1,
            end_column=end_column,
        )

    def _plain_text(self, node: DocNode) -> str:
        return (
            node.text if node.text else "".join(self._plain_text(child) for child in node.children)
        )

    def source_line(self, line_zero: int) -> str:
        if 0 <= line_zero < len(self.source_lines):
            return self.source_lines[line_zero]
        return ""

    def _unsupported(self, token: Token, base_line: int, column_offset: int) -> Exception:
        line = base_line + (token.map[0] if token.map else 0)
        return self._error(
            "HED-DOCS-0107",
            f"unsupported Markdown token: {token.type}",
            line,
            column_offset + 1,
        )

    def _error(self, code: str, message: str, line_zero: int, column: int) -> Exception:
        return source_error(
            code,
            message,
            self.source_path,
            line=line_zero + 1,
            column=column,
        )


class _InlineLocator:
    def __init__(self, parser: _Parser, token: Token, base_line: int, column_offset: int) -> None:
        self.parser = parser
        self.raw = token.content
        self.base_line = base_line + (token.map[0] if token.map else 0)
        self.column_offset = column_offset
        first_line = self.raw.splitlines()[0] if self.raw.splitlines() else self.raw
        original = parser.source_line(self.base_line)
        found = original.find(first_line)
        self.first_column = found + 1 if found >= 0 else column_offset + 1
        self.cursor = 0

    def find(self, value: str, *, start: int | None = None) -> int:
        position = self.raw.find(value, self.cursor if start is None else start)
        if position < 0:
            position = self.cursor if start is None else start
        self.cursor = max(self.cursor, position + len(value))
        return position

    def range_for(self, start: int, end: int) -> tuple[int, int, int, int]:
        before = self.raw[:start]
        through = self.raw[:end]
        start_line_offset = before.count("\n")
        end_line_offset = through.count("\n")
        start_column = (
            self.first_column + len(before.rsplit("\n", 1)[-1])
            if start_line_offset == 0
            else self.column_offset + len(before.rsplit("\n", 1)[-1]) + 1
        )
        end_column = (
            self.first_column + len(through.rsplit("\n", 1)[-1])
            if end_line_offset == 0
            else self.column_offset + len(through.rsplit("\n", 1)[-1]) + 1
        )
        if end_line_offset == start_line_offset:
            end_column = max(start_column, end_column)
        return (
            self.base_line + start_line_offset + 1,
            start_column,
            self.base_line + end_line_offset + 1,
            end_column,
        )

    def node(
        self,
        kind: str,
        start: int,
        end: int,
        *,
        text: str = "",
        attrs: dict[str, str] | None = None,
        children: tuple[DocNode, ...] = (),
    ) -> DocNode:
        line, column, end_line, end_column = self.range_for(start, end)
        return DocNode(
            kind=kind,
            text=text,
            attrs=tuple(sorted((attrs or {}).items())),
            children=children,
            source=self.parser.source_name,
            line=line,
            column=column,
            end_line=end_line,
            end_column=end_column,
        )


def slugify(text: str) -> str:
    """Return the deterministic NFKC/casefold heading identifier used by the compiler."""

    normalized = unicodedata.normalize("NFKC", text).casefold()
    value = re.sub(r"[^\w\s-]", "", normalized, flags=re.UNICODE).strip()
    return re.sub(r"[-\s]+", "-", value).strip("-") or "section"


def parse_markdown(
    source: str,
    *,
    source_path: Path,
    source_name: str | None = None,
    max_source_bytes: int = 2_000_000,
    max_nodes: int = 10_000,
    max_depth: int = 64,
    max_table_cells: int = 10_000,
    max_code_blocks: int = 200,
    max_code_block_bytes: int = 256_000,
    max_directives: int = 100,
) -> tuple[DocNode, ...]:
    """Parse supported Markdown into typed source-located nodes.

    ``source_name`` lets callers retain a jailed relative path in serialized manifests while
    keeping ``source_path`` for author-facing diagnostics.
    """

    limits = ParserLimits(
        max_source_bytes=max_source_bytes,
        max_nodes=max_nodes,
        max_depth=max_depth,
        max_table_cells=max_table_cells,
        max_code_blocks=max_code_blocks,
        max_code_block_bytes=max_code_block_bytes,
        max_directives=max_directives,
    )
    display_name = source_name if source_name is not None else str(source_path)
    return _Parser(source, source_path, display_name, limits).parse()
