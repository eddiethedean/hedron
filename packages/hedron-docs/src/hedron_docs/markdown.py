"""Markdown-to-document-AST adapter.

Python-Markdown supplies the well-tested block grammar. The resulting HTML is immediately parsed
into typed nodes; it is never emitted as trusted HTML. Source locations are deterministic line
estimates, sufficient for 0.1 diagnostics and improved by the source scanner where possible.
"""

from __future__ import annotations

import html as html_lib
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import markdown as markdown_lib

from .ast import DocNode
from .errors import source_error

_RAW_HTML = re.compile(r"<\s*/?\s*[A-Za-z][^>]*>")
_TAB_START = re.compile(r'^===\s+["\'](.+?)["\']\s*$')
_PLACEHOLDER = re.compile(r"^HEDRON_DOCS_TAB_[0-9A-F]{16}$")
_VOID_TAGS = frozenset({"br", "hr", "img"})
_STRUCTURAL_TAGS = frozenset(
    {"blockquote", "div", "li", "ol", "table", "tbody", "thead", "tr", "ul"}
)


def slugify(text: str) -> str:
    value = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip().lower()
    return re.sub(r"[-\s]+", "-", value) or "section"


def parse_markdown(
    source: str, *, source_path: Path, max_nodes: int = 10_000
) -> tuple[DocNode, ...]:
    if _RAW_HTML.search(source):
        match = _RAW_HTML.search(source)
        assert match is not None
        line = source.count("\n", 0, match.start()) + 1
        raise source_error(
            "HED-DOCS-0100",
            "raw HTML is not supported; use Markdown components",
            source_path,
            line=line,
        )
    tabs: dict[str, DocNode] = {}
    normalized = _extract_tabs(source, tabs, source_path, max_nodes=max_nodes)
    rendered = markdown_lib.markdown(
        normalized,
        extensions=["fenced_code", "tables", "admonition"],
        output_format="html",
    )
    parser = _TreeParser(source, source_path, tabs)
    parser.feed(rendered)
    parser.close()
    nodes = _deduplicate_heading_ids(tuple(parser.nodes))
    node_count = _count_nodes(nodes)
    if node_count > max_nodes:
        raise source_error(
            "HED-DOCS-0101", f"document exceeds node limit ({max_nodes})", source_path
        )
    return nodes


def _extract_tabs(
    source: str, tabs: dict[str, DocNode], source_path: Path, *, max_nodes: int
) -> str:
    lines = source.splitlines()
    output: list[str] = []
    index = 0
    tab_index = 0
    while index < len(lines):
        match = _TAB_START.match(lines[index])
        if not match:
            output.append(lines[index])
            index += 1
            continue
        panels: list[tuple[str, DocNode]] = []
        while index < len(lines):
            heading = _TAB_START.match(lines[index])
            if not heading:
                break
            label = heading.group(1).strip()
            start_line = index + 1
            index += 1
            panel_lines: list[str] = []
            while index < len(lines) and not _TAB_START.match(lines[index]):
                line = lines[index]
                if line.startswith("    "):
                    panel_lines.append(line[4:])
                elif not line.strip():
                    panel_lines.append("")
                else:
                    break
                index += 1
            panel_nodes = parse_markdown(
                "\n".join(panel_lines), source_path=source_path, max_nodes=max_nodes
            )
            panels.append(
                (label, DocNode("tab-panel", text=label, children=panel_nodes, line=start_line))
            )
        key = f"HEDRON_DOCS_TAB_{tab_index:016X}"
        tab_index += 1
        tabs[key] = DocNode(
            "tabs",
            children=tuple(panel for _, panel in panels),
            line=panels[0][1].line if panels else 1,
        )
        output.append(key)
    return "\n".join(output)


class _TreeParser(HTMLParser):
    def __init__(self, source: str, source_path: Path, tabs: dict[str, DocNode]) -> None:
        super().__init__(convert_charrefs=True)
        self.source = source
        self.source_path = source_path
        self.tabs = tabs
        self._stack: list[dict[str, Any]] = []
        self.nodes: list[DocNode] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized_tag = tag.lower()
        self._stack.append(
            {
                "tag": normalized_tag,
                "attrs": {key: value or "" for key, value in attrs},
                "children": [],
            }
        )
        if normalized_tag in _VOID_TAGS:
            self.handle_endtag(normalized_tag)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if not self._stack:
            return
        item = self._stack.pop()
        item["parent"] = self._stack[-1]["tag"] if self._stack else ""
        node = self._node(item)
        if self._stack:
            self._stack[-1]["children"].append(node)
        else:
            self.nodes.append(node)

    def handle_data(self, data: str) -> None:
        if self._stack:
            if data.isspace() and self._stack[-1]["tag"] in _STRUCTURAL_TAGS:
                return
            self._stack[-1]["children"].append(DocNode("text", text=data, line=self._line(data)))
        elif data.strip():
            self.nodes.append(DocNode("paragraph", text=data.strip(), line=self._line(data)))

    def _node(self, item: dict[str, Any]) -> DocNode:
        tag = item["tag"]
        attrs = tuple(sorted((str(key), str(value)) for key, value in item["attrs"].items()))
        children = tuple(item["children"])
        text = "".join(_node_text(child) for child in children)
        line = self._line(text)
        if _PLACEHOLDER.fullmatch(text):
            return self.tabs[text]
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            return DocNode(
                "heading",
                text=text,
                attrs=(("level", tag[1]), ("id", slugify(text))),
                children=children,
                line=line,
            )
        if tag == "p":
            return DocNode("paragraph", text=text, children=children, line=line)
        if tag in {"strong", "b"}:
            return DocNode("strong", text=text, children=children, line=line)
        if tag in {"em", "i"}:
            return DocNode("emphasis", text=text, children=children, line=line)
        if tag == "code" and item.get("parent") != "pre":
            return DocNode("inline-code", text=text, line=line)
        if tag == "pre":
            code = text
            language = ""
            if children and children[0].kind == "code":
                language = children[0].attr("language")
            return DocNode("code", text=code, attrs=(("language", language),), line=line)
        if tag == "ul" or tag == "ol":
            return DocNode(
                "list",
                attrs=(("ordered", "true" if tag == "ol" else "false"),),
                children=children,
                line=line,
            )
        if tag == "li":
            return DocNode("list-item", text=text, children=children, line=line)
        if tag == "blockquote":
            return DocNode("quote", text=text, children=children, line=line)
        if tag == "hr":
            return DocNode("divider", line=line)
        if tag == "a":
            return DocNode("link", text=text, attrs=attrs, children=children, line=line)
        if tag == "img":
            return DocNode("image", attrs=attrs, line=line)
        if tag == "table":
            return DocNode("table", children=children, line=line)
        if tag in {"thead", "tbody", "tr", "th", "td"}:
            return DocNode(tag, text=text, children=children, line=line)
        if tag == "div" and "admonition" in item["attrs"].get("class", ""):
            classes = item["attrs"].get("class", "").split()
            tone = next(
                (
                    x
                    for x in ("note", "info", "success", "warning", "danger", "tip")
                    if x in classes
                ),
                "info",
            )
            if tone == "note" or tone == "tip":
                tone = "info"
            title = children[0].text if children and children[0].kind == "paragraph" else ""
            body = children[1:] if title else children
            return DocNode(
                "alert",
                text=" ".join(_node_text(child) for child in body),
                attrs=(("tone", tone), ("title", title)),
                children=body,
                line=line,
            )
        if tag == "div":
            return DocNode("container", children=children, line=line)
        if tag == "span":
            return DocNode("span", text=text, children=children, line=line)
        if tag == "br":
            return DocNode("break", line=line)
        if tag == "code":
            classes = item["attrs"].get("class", "")
            language = classes.removeprefix("language-") if classes.startswith("language-") else ""
            return DocNode("code", text=text, attrs=(("language", language),), line=line)
        return DocNode("container", text=text, children=children, line=line)

    def _line(self, text: str) -> int:
        if not text:
            return 1
        position = self.source.find(html_lib.unescape(text.strip()))
        return self.source.count("\n", 0, position) + 1 if position >= 0 else 1


def _node_text(node: DocNode) -> str:
    return node.text or "".join(_node_text(child) for child in node.children)


def _count_nodes(nodes: tuple[DocNode, ...]) -> int:
    count = 0
    pending = list(nodes)
    while pending:
        node = pending.pop()
        count += 1
        pending.extend(node.children)
    return count


def _deduplicate_heading_ids(nodes: tuple[DocNode, ...]) -> tuple[DocNode, ...]:
    counts: dict[str, int] = {}

    def normalize(node: DocNode) -> DocNode:
        attrs = dict(node.attrs)
        if node.kind == "heading":
            base = attrs.get("id") or slugify(node.text)
            counts[base] = counts.get(base, 0) + 1
            attrs["id"] = base if counts[base] == 1 else f"{base}-{counts[base]}"
        return DocNode(
            kind=node.kind,
            text=node.text,
            attrs=tuple(sorted(attrs.items())),
            children=tuple(normalize(child) for child in node.children),
            line=node.line,
        )

    return tuple(normalize(node) for node in nodes)
