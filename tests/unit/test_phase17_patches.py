"""Phase 0.17 PATCH-017: PropertyPatch / CollectionPatch bounded ops."""

from __future__ import annotations

import pytest

from hedron_core import (
    CollectionPatch,
    CollectionSelector,
    PatchError,
    PatchOp,
    PropertyPatch,
    apply_property_patch,
    full_fragment_fallback_required,
)
from hedron_core.codes import HED_PATCH_0002, HED_PATCH_0003


def test_assign_merge_append() -> None:
    state = {
        "chart": {"_version": 1, "title": "A", "meta": {"a": 1}, "series": [1]},
    }
    assigned = apply_property_patch(
        state,
        PropertyPatch(target_id="chart", path="title", op=PatchOp.ASSIGN, value="B"),
    )
    assert assigned["chart"]["title"] == "B"
    assert state["chart"]["title"] == "A"  # original untouched

    merged = apply_property_patch(
        assigned,
        PropertyPatch(
            target_id="chart",
            path="meta",
            op="merge",
            value={"b": 2},
        ),
    )
    assert merged["chart"]["meta"] == {"a": 1, "b": 2}

    appended = apply_property_patch(
        merged,
        PropertyPatch(target_id="chart", path="series", op=PatchOp.APPEND, value=2),
    )
    assert appended["chart"]["series"] == [1, 2]


def test_version_mismatch() -> None:
    state = {"store": {"_version": 3, "value": 1}}
    with pytest.raises(PatchError, match="Version mismatch") as excinfo:
        apply_property_patch(
            state,
            PropertyPatch(
                target_id="store",
                path="value",
                op=PatchOp.ASSIGN,
                value=2,
                expected_version=2,
            ),
        )
    assert excinfo.value.code == HED_PATCH_0002
    assert full_fragment_fallback_required(excinfo.value) is True


def test_oversized_payload_fails() -> None:
    state = {"store": {"_version": 1, "blob": ""}}
    huge = "x" * 1000
    with pytest.raises(PatchError, match="max_bytes") as excinfo:
        apply_property_patch(
            state,
            PropertyPatch(target_id="store", path="blob", op=PatchOp.ASSIGN, value=huge),
            max_bytes=64,
        )
    assert excinfo.value.code == HED_PATCH_0003
    assert full_fragment_fallback_required(excinfo.value) is True


def test_fallback_helper_false_for_unrelated() -> None:
    assert full_fragment_fallback_required(ValueError("nope")) is False
    assert full_fragment_fallback_required(RuntimeError("x")) is False


def test_collection_types_construct() -> None:
    selector = CollectionSelector(kind="exact_member", member_id="row-1")
    patch = CollectionPatch(
        collection_id="grid",
        selector=selector,
        op=PatchOp.ASSIGN,
        value={"selected": True},
        path="props",
    )
    assert patch.collection_id == "grid"
    assert patch.selector.kind == "exact_member"
