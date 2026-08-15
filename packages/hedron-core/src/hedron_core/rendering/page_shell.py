"""PAGE document wrapping without importing Page."""

from __future__ import annotations

from hedron_core._nodes import Node
from hedron_core._serializer import escape_attr, serialize_tree
from hedron_core.component import NodeLike

DOCUMENT_SHELL_ATTR = "hedron_document_shell"


def is_document_shell(value: object) -> bool:
    """True when ``value`` is a full HTML document component (Page)."""
    return bool(getattr(type(value), DOCUMENT_SHELL_ATTR, False))


def serialize_page_or_fragment(
    value: NodeLike,
    nodes: tuple[Node, ...],
    *,
    mount_path: str,
    locale: str,
    page_mode: bool,
) -> str:
    if page_mode:
        if is_document_shell(value):
            html_text = serialize_tree(nodes, mount_path=mount_path)
            if not html_text.lstrip().lower().startswith("<!doctype"):
                html_text = "<!DOCTYPE html>" + html_text
        else:
            body_html = serialize_tree(nodes, mount_path=mount_path)
            html_text = (
                "<!DOCTYPE html>"
                f'<html lang="{escape_attr(locale)}">'
                '<head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1">'
                "</head>"
                f"<body>{body_html}</body></html>"
            )
        return html_text
    return serialize_tree(nodes, mount_path=mount_path)
