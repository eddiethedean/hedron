"""Lower the manifest AST into native Hedron content components."""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Literal, cast
from urllib.parse import urlsplit

from hedron import Alert, ClipboardCopy, CodeViewer, Heading, Image, Link, Table, Tabs
from hedron_core.component import NodeLike
from hedron_core.html import html
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.typing_aliases import HtmlAttrValue

from .ast import DocNode

_ANCHOR_ID = re.compile(r"^[A-Za-z][\w:.-]*$", re.UNICODE)
_MAX_COPY_CHARS = 100_000
_TRUNCATION_SUFFIX = "\n… [truncated]"

# No raw/trusted HTML is admitted by the W3 renderer.  Keeping the registry explicit makes that
# boundary auditable if a future docs-local compatibility node is ever approved.
COMPATIBILITY_NODE_REGISTRY: frozenset[str] = frozenset()


def render_document(nodes: Sequence[DocNode]) -> NodeLike:
    """Render a sequence without introducing an opaque document-body node."""

    return [render_node(node) for node in nodes]


def render_node(node: DocNode) -> NodeLike:
    """Render one closed AST node through Hedron or safe native HTML primitives."""

    kind = node.kind
    if kind == "heading":
        return _render_heading(node)
    if kind == "paragraph":
        return _render_content_element("p", node)
    if kind == "code":
        return _render_code(node)
    if kind == "list":
        return _render_list(node)
    if kind == "list-item":
        return _render_children_or_text(node)
    if kind == "quote":
        return html.blockquote(*_children_or_text(node))
    if kind == "divider":
        return html.hr()
    if kind == "link":
        return _render_link(node)
    if kind == "image":
        src = node.attr("src") or "/"
        external = bool(urlsplit(src).scheme or urlsplit(src).netloc)
        title = node.attr("title")
        if title:
            return html.img(
                src=SafeUrl.parse(src, purpose=UrlPurpose.ASSET, allow_external=external),
                alt=node.attr("alt", ""),
                title=title,
            )
        return Image(src, alt=node.attr("alt", ""), allow_external=external)
    if kind == "alert":
        return _render_alert(node)
    if kind == "details":
        return html.details(
            html.summary(node.attr("title") or "Details"),
            *_children_or_text(node),
            open=node.attr("open") == "true" or None,
            class_="hedron-doc-details",
        )
    if kind == "tabs":
        panels = [
            (panel.text or _plain_text(panel), render_document(panel.children))
            for panel in node.children
        ]
        return Tabs(*panels, responsive="scroll", class_="hedron-doc-tabs")
    if kind == "table":
        return _render_table(node)
    if kind == "definition-list":
        return html.dl(*_children_or_text(node))
    if kind == "dt":
        return _render_content_element("dt", node)
    if kind == "dd":
        return _render_content_element("dd", node)
    if kind == "footnotes":
        return html.section(
            html.h2("Footnotes", class_="sr-only"),
            html.ol(*_children_or_text(node)),
            aria={"label": "Footnotes"},
            class_="hedron-doc-footnotes",
        )
    if kind == "footnote":
        label = node.attr("label")
        return html.li(*_children_or_text(node), id=f"fn-{label}")
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
            class_="hedron-doc-footnote-backref",
        )
    if kind == "api-directive":
        return html.div(
            html.strong("API reference"),
            html.code(node.attr("target")),
            class_="hedron-docs-api-directive",
            data={"hedron-docs-node": "api"},
        )
    if kind == "demo-directive":
        return html.div(
            html.strong("Interactive demo"),
            html.code(node.attr("id")),
            class_="hedron-docs-demo-directive",
            data={"hedron-docs-node": "demo"},
        )
    if kind in {"text", "strong", "emphasis", "inline-code", "span", "break"}:
        return _render_inline(node)
    if kind == "container":
        return html.div(*_children_or_text(node), class_="hedron-doc-container")
    if kind == "thead":
        return html.thead(*_children_or_text(node))
    if kind == "tbody":
        return html.tbody(*_children_or_text(node))
    if kind == "tr":
        return html.tr(*_children_or_text(node))
    if kind == "th":
        return html.th(*_children_or_text(node), scope="col")
    if kind == "td":
        return html.td(*_children_or_text(node))
    raise ValueError(f"unsupported document node kind: {kind!r}")


def _render_heading(node: DocNode) -> NodeLike:
    heading_id = node.attr("id")
    aliases = _aliases(node.attr("aliases"))
    anchors: list[NodeLike] = [_anchor(heading_id, canonical=True)]
    anchors.extend(_anchor(alias, canonical=False) for alias in aliases)
    level = cast(Literal[1, 2, 3, 4, 5, 6], max(1, min(6, int(node.attr("level", "2")))))
    if node.children and not all(child.kind == "text" for child in node.children):
        heading: NodeLike = getattr(html, f"h{level}")(
            *_children_or_text(node), class_="hedron-heading"
        )
    else:
        heading = Heading(node.text, level=level)
    return html.div(
        *anchors,
        heading,
        class_="hedron-doc-heading",
        data={"hedron-fragment-target": "true"},
    )


def _anchor(value: str, *, canonical: bool) -> NodeLike:
    if not _ANCHOR_ID.fullmatch(value):
        raise ValueError(f"invalid document anchor id: {value!r}")
    attrs: dict[str, HtmlAttrValue] = {
        "id": value,
        "class_": "hedron-doc-anchor",
        "tabindex": "-1",
        "aria": {"hidden": "true"},
    }
    if canonical:
        attrs["href"] = SafeUrl.parse(f"#{value}", purpose=UrlPurpose.NAVIGATION)
    return html.a(**attrs)


def _render_content_element(tag: str, node: DocNode) -> NodeLike:
    return getattr(html, tag)(*_children_or_text(node))


def _render_code(node: DocNode) -> NodeLike:
    language = node.attr("language")
    label = language or "text"
    displayed = _clip_code(node.text)
    toolbar = html.div(
        html.span(label, class_="hedron-doc-code-language", data={"language": label}),
        ClipboardCopy(displayed, label="Copy code"),
        class_="hedron-doc-code-toolbar",
    )
    return html.figure(
        html.figcaption(f"{label} code example", class_="sr-only"),
        toolbar,
        CodeViewer(displayed, language=language or None),
        class_="hedron-doc-code",
        data={"hedron-code-block": "true", "language": label},
    )


def _clip_code(text: str) -> str:
    if len(text) <= _MAX_COPY_CHARS:
        return text
    prefix_length = max(0, _MAX_COPY_CHARS - len(_TRUNCATION_SUFFIX))
    return text[:prefix_length] + _TRUNCATION_SUFFIX


def _render_list(node: DocNode) -> NodeLike:
    items = [html.li(*_children_or_text(item)) for item in node.children]
    attrs: dict[str, HtmlAttrValue] = {"class_": "hedron-doc-list"}
    if node.attr("ordered") == "true":
        attrs["start"] = node.attr("start") or None
        return html.ol(*items, **attrs)
    return html.ul(*items, **attrs)


def _render_link(node: DocNode) -> NodeLike:
    href = _link_href(node.attr("href") or "/")
    external = bool(urlsplit(href).scheme or urlsplit(href).netloc)
    children = _children_or_text(node)
    if not node.children or all(child.kind == "text" for child in node.children):
        label = node.text or _plain_text(node) or href
        if not node.attr("title"):
            return Link(label, href, external=external)
        attrs: dict[str, HtmlAttrValue] = {
            "href": SafeUrl.parse(href, purpose=UrlPurpose.NAVIGATION, allow_external=external),
            "title": node.attr("title"),
        }
        if external:
            attrs.update({"rel": "noopener noreferrer", "target": "_blank"})
        return html.a(label, **attrs)
    attrs: dict[str, HtmlAttrValue] = {
        "href": SafeUrl.parse(href, purpose=UrlPurpose.NAVIGATION, allow_external=external)
    }
    if external:
        attrs.update({"rel": "noopener noreferrer", "target": "_blank"})
    if node.attr("title"):
        attrs["title"] = node.attr("title")
    return html.a(*children, **attrs)


def _render_alert(node: DocNode) -> NodeLike:
    tone = cast(Literal["info", "success", "warning", "danger"], node.attr("tone", "info"))
    title = node.attr("title") or None
    if not node.children or all(child.kind == "text" for child in node.children):
        return Alert(node.text, tone=tone, title=title)
    parts: list[NodeLike] = []
    if title:
        parts.append(html.strong(title))
    parts.append(html.div(*_children_or_text(node), class_="hedron-alert-body"))
    return html.div(
        *parts,
        class_=f"hedron-alert hedron-alert-{tone}",
        role="alert" if tone == "danger" else "status",
        data={"hedron-tone": tone},
    )


def _render_table(node: DocNode) -> NodeLike:
    headers: list[NodeLike] = []
    rows: list[list[NodeLike]] = []
    for section in node.children:
        if section.kind not in {"thead", "tbody"}:
            continue
        for row in section.children:
            cells = [cell for cell in row.children if cell.kind in {"th", "td"}]
            if section.kind == "thead":
                headers = [_cell_content(cell) for cell in cells]
            elif cells:
                rows.append([_cell_content(cell) for cell in cells])
    return Table(headers=headers, rows=rows, responsive="scroll")


def _cell_content(node: DocNode) -> NodeLike:
    children = _children_or_text(node)
    return children[0] if len(children) == 1 else children


def _render_inline(node: DocNode) -> NodeLike:
    if node.kind == "text":
        return node.text
    if node.kind == "strong":
        return html.strong(*_children_or_text(node))
    if node.kind == "emphasis":
        return html.em(*_children_or_text(node))
    if node.kind == "inline-code":
        return html.code(node.text)
    if node.kind == "break":
        return html.br()
    return html.span(*_children_or_text(node))


def _children_or_text(node: DocNode) -> list[NodeLike]:
    if node.children:
        return [render_node(child) for child in node.children]
    return [node.text] if node.text else []


def _render_children_or_text(node: DocNode) -> NodeLike:
    children = _children_or_text(node)
    return children if len(children) != 1 else children[0]


def _plain_text(node: DocNode) -> str:
    if node.text and not node.children:
        return node.text
    return "".join(_plain_text(child) for child in node.children) or node.text


def _aliases(value: str) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(item for item in (part.strip() for part in value.split(",")) if item)


def _link_href(href: str) -> str:
    if href.startswith(("#", "http://", "https://", "mailto:", "tel:")):
        return href
    if "#" in href:
        path, fragment = href.split("#", 1)
        return (path.rstrip("/") or "/") + "#" + fragment
    return href.rstrip("/") or "/"
