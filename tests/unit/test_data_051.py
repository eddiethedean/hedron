"""DATA-051 TreeView and Typeahead identities, abort, fallback."""

from __future__ import annotations

import pytest

from hedron.testing import assert_renders
from hedron_extras.composition import TreeView
from hedron_extras.editors import Typeahead


def test_treeview_stable_ids_and_fallback() -> None:
    html = assert_renders(
        TreeView([{"id": "a", "label": "A", "children": [{"id": "b", "label": "B"}]}], name="tree"),
        contains='data-abortable="true"',
    )
    assert "hedron-extras-composition" in html
    assert "__fallback" in html
    with pytest.raises(ValueError, match="unique"):
        TreeView([{"id": "a", "label": "A"}, {"id": "a", "label": "Dup"}])
    empty = assert_renders(TreeView([], empty_message="No items"), contains="No items")
    assert "No items" in empty
    err = assert_renders(TreeView([], error_message="offline"), contains="offline")
    assert "__retry" in err


def test_typeahead_page_abort_and_select_fallback() -> None:
    html = assert_renders(
        Typeahead("q", ["alpha", "beta"], page_size=1, source="/search"),
        contains="hedron-extras-typeahead",
    )
    assert "__fallback" in html
    assert 'data-abortable="true"' in html
    assert "alpha" in html
    assert "beta" not in html  # paged
    with pytest.raises(ValueError, match="javascript"):
        Typeahead("q", ["a"], source="javascript:alert(1)")
    with pytest.raises(ValueError, match="page_size"):
        Typeahead("q", ["a"], page_size=0)
