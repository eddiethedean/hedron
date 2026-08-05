"""PARITY-014: accelerator absence preserves semantics."""

from __future__ import annotations

from hedron_core._serializer import escape_attr, escape_text
from hedron_native import escape_attr_python, escape_text_python


def test_core_escape_matches_python_reference() -> None:
    samples = ["", "x", "<a>&", "q\"w'e", "nul\x00byte", "café <tag>"]
    for sample in samples:
        assert escape_text(sample) == escape_text_python(sample)
        assert escape_attr(sample) == escape_attr_python(sample)


def test_serialize_tree_deterministic_with_or_without_native() -> None:
    from hedron_core._nodes import ElementNode, TextNode
    from hedron_core._serializer import serialize_node

    node = ElementNode(
        tag="p",
        attributes={"class": "x", "title": "a&b"},
        children=(TextNode(text="<hi>"),),
        void=False,
    )
    html = serialize_node(node)
    assert html == '<p class="x" title="a&amp;b">&lt;hi&gt;</p>'
