"""Lower manifest nodes into native Hedron components."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal, cast
from urllib.parse import urlsplit

from hedron import Alert, CodeBlock, Heading, Image, Link, List, Table, Tabs
from hedron_core.component import NodeLike
from hedron_core.html import html
from hedron_core.security import SafeUrl, UrlPurpose

from .ast import DocNode


def render_document(nodes: Sequence[DocNode]) -> NodeLike:
    return [render_node(node) for node in nodes]


def render_node(node: DocNode) -> NodeLike:
    kind = node.kind
    if kind == "heading":
        level = cast(
            Literal[1, 2, 3, 4, 5, 6],
            max(1, min(6, int(node.attr("level", "2")))),
        )
        # Heading's typed props intentionally do not expose arbitrary ids; the anchor is a
        # separate semantic native element immediately before the heading.
        return html.div(
            html.a(
                id=node.attr("id"),
                href=SafeUrl.parse(f"#{node.attr('id')}", purpose=UrlPurpose.NAVIGATION),
                aria={"hidden": "true"},
            ),
            Heading(node.text, level=level),
            class_="hedron-doc-heading",
        )
    if kind == "paragraph":
        return html.p(
            *(render_node(child) for child in node.children),
            node.text if not node.children else None,
        )
    if kind == "code":
        return CodeBlock(node.text, language=node.attr("language") or None)
    if kind == "list":
        return List(
            *(render_node(child) for child in node.children), ordered=node.attr("ordered") == "true"
        )
    if kind == "list-item":
        return [render_node(child) for child in node.children] if node.children else node.text
    if kind == "quote":
        return html.blockquote(*(render_node(child) for child in node.children))
    if kind == "divider":
        return html.hr()
    if kind == "link":
        href = _link_href(node.attr("href") or "/")
        external = bool(urlsplit(href).scheme or urlsplit(href).netloc)
        return Link(node.text or href, href, external=external)
    if kind == "image":
        src = node.attr("src") or "/"
        external = bool(urlsplit(src).scheme or urlsplit(src).netloc)
        return Image(src, alt=node.attr("alt", ""), allow_external=external)
    if kind == "alert":
        tone = cast(Literal["info", "success", "warning", "danger"], node.attr("tone", "info"))
        return Alert(node.text, tone=tone, title=node.attr("title") or None)
    if kind == "details":
        return html.details(
            html.summary(node.attr("title") or "Details"),
            *(render_node(child) for child in node.children),
            open=node.attr("open") == "true" or None,
        )
    if kind == "tabs":
        return Tabs(*[(panel.text, render_document(panel.children)) for panel in node.children])
    if kind == "table":
        return _render_table(node)
    if kind == "definition-list":
        return html.dl(*(render_node(child) for child in node.children))
    if kind == "dt":
        return html.dt(*(render_node(child) for child in node.children))
    if kind == "dd":
        return html.dd(*(render_node(child) for child in node.children))
    if kind == "footnotes":
        return html.section(
            html.h2("Footnotes", class_="sr-only"),
            html.ol(*(render_node(child) for child in node.children)),
            aria={"label": "Footnotes"},
        )
    if kind == "footnote":
        label = node.attr("label")
        return html.li(
            *(render_node(child) for child in node.children),
            id=f"fn-{label}",
        )
    if kind == "footnote-ref":
        label = node.attr("label")
        return html.sup(
            html.a(
                label,
                id=f"fnref-{label}",
                href=SafeUrl.parse(f"#fn-{label}", purpose=UrlPurpose.NAVIGATION),
                aria={"label": f"Footnote {label}"},
            )
        )
    if kind == "footnote-backref":
        label = node.attr("label")
        return html.a(
            "Back to reference",
            href=SafeUrl.parse(f"#fnref-{label}", purpose=UrlPurpose.NAVIGATION),
        )
    if kind == "api-directive":
        return html.div(
            html.strong("API reference"),
            html.code(node.attr("target")),
            class_="hedron-docs-api-directive",
        )
    if kind == "demo-directive":
        return html.div(
            html.strong("Interactive demo"),
            html.code(node.attr("id")),
            class_="hedron-docs-demo-directive",
        )
    if kind in {"text", "strong", "emphasis", "inline-code", "span", "break"}:
        return _render_inline(node)
    return html.div(
        *(render_node(child) for child in node.children), node.text if not node.children else None
    )


def _render_inline(node: DocNode) -> NodeLike:
    if node.kind == "text":
        return node.text
    if node.kind == "link":
        href = _link_href(node.attr("href") or "/")
        return Link(
            node.text or href, href, external=bool(urlsplit(href).scheme or urlsplit(href).netloc)
        )
    if node.kind == "strong":
        return html.strong(
            *(render_node(child) for child in node.children),
            node.text if not node.children else None,
        )
    if node.kind == "emphasis":
        return html.em(
            *(render_node(child) for child in node.children),
            node.text if not node.children else None,
        )
    if node.kind == "inline-code":
        return html.code(node.text)
    if node.kind == "break":
        return html.br()
    if node.kind == "image":
        return render_node(node)
    return [render_node(child) for child in node.children] if node.children else node.text


def _render_table(node: DocNode) -> NodeLike:
    headers: list[str] = []
    rows: list[list[str]] = []
    for section in node.children:
        if section.kind not in {"thead", "tbody"}:
            continue
        for row in section.children:
            cells = [cell.text for cell in row.children if cell.kind in {"th", "td"}]
            if section.kind == "thead":
                headers = cells
            elif cells:
                rows.append(cells)
    return Table(headers=headers, rows=rows, responsive="scroll")


def _link_href(href: str) -> str:
    if href.startswith(("#", "http://", "https://", "mailto:", "tel:")):
        return href
    if "#" in href:
        path, fragment = href.split("#", 1)
        return (path.rstrip("/") or "/") + "#" + fragment
    return href.rstrip("/") or "/"
