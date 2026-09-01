"""Exhaustive bounded mutation matrices for hedron-core patches."""

from __future__ import annotations

from typing import Any

import pytest

from hedron_core.patches import (
    PatchError,
    PatchOp,
    PropertyPatch,
    apply_property_patch,
    full_fragment_fallback_required,
)


def _state() -> dict[str, object]:
    return {
        "target": {
            "_version": 3,
            "title": "old",
            "meta": {"a": 1},
            "items": ["a", "b", "c"],
            "count": 5,
            "scalar": "value",
        },
        "other": {"untouched": [1, 2]},
    }


@pytest.mark.parametrize(
    ("path", "op", "value", "expected"),
    [
        ("title", PatchOp.ASSIGN, "new", "new"),
        ("meta", PatchOp.MERGE, {"b": 2}, {"a": 1, "b": 2}),
        ("created", PatchOp.MERGE, {"a": 1}, {"a": 1}),
        ("items", PatchOp.APPEND, "d", ["a", "b", "c", "d"]),
        ("items", PatchOp.PREPEND, "z", ["z", "a", "b", "c"]),
        ("items", PatchOp.EXTEND, ("d", "e"), ["a", "b", "c", "d", "e"]),
        (
            "items",
            PatchOp.INSERT,
            {"index": 1, "item": "x"},
            ["a", "x", "b", "c"],
        ),
        ("items", PatchOp.REMOVE, "b", ["a", "c"]),
        ("meta.a", PatchOp.DELETE, None, {}),
        ("items.1", PatchOp.DELETE, None, ["a", "c"]),
        ("items", PatchOp.CLEAR, None, []),
        ("scalar", PatchOp.CLEAR, None, {}),
        ("items", PatchOp.REORDER, [2, 0, 1], ["c", "a", "b"]),
        ("items", PatchOp.REVERSE, None, ["c", "b", "a"]),
        ("count", PatchOp.INCREMENT, None, 6),
        ("count", PatchOp.INCREMENT, 2.5, 7.5),
        ("count", PatchOp.DECREMENT, None, 4),
        ("count", PatchOp.DECREMENT, 2, 3),
        ("count", PatchOp.CLAMP, {"min": 0, "max": 3}, 3),
        ("count", PatchOp.CLAMP, {"min": 7}, 7),
    ],
)
def test_patch_operation_matrix(
    path: str,
    op: PatchOp,
    value: object,
    expected: object,
) -> None:
    original = _state()
    result = apply_property_patch(
        original,
        PropertyPatch("target", path, op, value, expected_version=3),
    )
    target = result["target"]
    assert isinstance(target, dict)
    key = path.split(".")[0]
    assert target.get(key) == expected
    assert original == _state()
    assert result["other"] == original["other"]
    assert result["other"] is not original["other"]


def test_root_assign_and_clear_require_mapping_semantics() -> None:
    assigned = apply_property_patch(
        _state(), PropertyPatch("target", ".", "assign", {"replacement": True})
    )
    assert assigned["target"] == {"replacement": True}

    cleared = apply_property_patch(_state(), PropertyPatch("target", "/", "clear"))
    assert cleared["target"] == {}


def test_list_paths_create_missing_slots_for_assignment() -> None:
    result = apply_property_patch(_state(), PropertyPatch("target", "items.5", "assign", "last"))
    assert result["target"]["items"] == ["a", "b", "c", None, None, "last"]


@pytest.mark.parametrize(
    ("patch", "kwargs", "message"),
    [
        (PropertyPatch("target", "title", "unknown"), {}, "Unknown patch op"),
        (PropertyPatch("missing", "title", "assign", "x"), {}, "Unknown patch target"),
        (
            PropertyPatch("target", "title", "assign", "x", expected_version=2),
            {},
            "Version mismatch",
        ),
        (PropertyPatch("target", "meta", "merge", []), {}, "merge requires a mapping"),
        (PropertyPatch("target", "title", "merge", {"a": 1}), {}, "merge target"),
        (PropertyPatch("target", "items", "extend", "bad"), {}, "extend requires"),
        (PropertyPatch("target", "items", "insert", {}), {}, "insert requires"),
        (
            PropertyPatch("target", "items", "insert", {"index": True, "item": "x"}),
            {},
            "index must be an integer",
        ),
        (PropertyPatch("target", "items", "remove", "missing"), {}, "not present"),
        (PropertyPatch("target", "missing", "delete"), {}, "not present"),
        (PropertyPatch("target", "", "delete"), {}, "non-empty path"),
        (PropertyPatch("target", "items.9", "delete"), {}, "not present"),
        (PropertyPatch("target", "items", "reorder", "bad"), {}, "sequence of indices"),
        (PropertyPatch("target", "items", "reorder", [0, True, 2]), {}, "must be integers"),
        (PropertyPatch("target", "items", "reorder", [0, 0, 1]), {}, "permutation"),
        (PropertyPatch("target", "title", "reverse"), {}, "list target"),
        (PropertyPatch("target", "title", "increment"), {}, "numeric current"),
        (PropertyPatch("target", "count", "increment", True), {}, "numeric current and delta"),
        (PropertyPatch("target", "title", "decrement"), {}, "numeric current"),
        (PropertyPatch("target", "title", "clamp", {}), {}, "numeric current"),
        (PropertyPatch("target", "count", "clamp", []), {}, "requires {'min'"),
        (
            PropertyPatch("target", "count", "clamp", {"min": "low", "max": 9}),
            {},
            "must be numeric",
        ),
        (PropertyPatch("target", "title.child", "assign", 1), {}, "mapping or list"),
        (PropertyPatch("target", "items.bad", "assign", 1), {}, "Failed to apply"),
        (PropertyPatch("target", "", "assign", []), {}, "non-mapping value"),
        (PropertyPatch("target", "title", "assign", "x"), {"max_ops": 0}, "max_ops"),
        (PropertyPatch("target", "title", "assign", "x"), {"max_bytes": 0}, "max_bytes"),
        (
            PropertyPatch("target", "deep.path", "assign", "x"),
            {"max_ops": 2},
            "operation cost",
        ),
        (
            PropertyPatch("target", "title", "assign", "long value"),
            {"max_bytes": 3},
            "payload",
        ),
    ],
)
def test_patch_failure_matrix(
    patch: PropertyPatch,
    kwargs: dict[str, Any],
    message: str,
) -> None:
    with pytest.raises(PatchError, match=message) as raised:
        apply_property_patch(_state(), patch, **kwargs)
    assert raised.value.diagnostic is not None
    assert full_fragment_fallback_required(raised.value) is True


def test_patch_rejects_non_mapping_target_state_and_non_string_keys() -> None:
    with pytest.raises(PatchError, match="state must be a mapping"):
        apply_property_patch({"target": []}, PropertyPatch("target", "x", "assign", 1))
    with pytest.raises(PatchError, match="state must be a mapping"):
        apply_property_patch({"target": {1: "bad"}}, PropertyPatch("target", "x", "assign", 1))


def test_custom_nonfallback_patch_error_does_not_request_fragment() -> None:
    error = PatchError("custom", code="CUSTOM", fallback=False)
    assert full_fragment_fallback_required(error) is False
