"""Versioned, bounded property and collection patches (RFC-0041 / PATCH-017).

Patches mutate declared component/store state only. Invalid, stale, unauthorized, or
oversized patches fail closed; callers must fall back to a full-fragment refresh when
``full_fragment_fallback_required`` returns True.
"""

from __future__ import annotations

import copy
import json
from collections.abc import Mapping, MutableMapping, Sequence
from dataclasses import dataclass
from typing import Literal, TypeGuard, cast

from hedron_core.codes import (
    HED_PATCH_0001,
    HED_PATCH_0002,
    HED_PATCH_0003,
    HED_PATCH_0004,
)
from hedron_core.compat import StrEnum
from hedron_core.diagnostics import HedronError, error
from hedron_core.typing_aliases import is_object_list, is_string_mapping

__all__ = [
    "CollectionPatch",
    "CollectionSelector",
    "CollectionSelectorKind",
    "PatchError",
    "PatchOp",
    "PropertyPatch",
    "apply_property_patch",
    "full_fragment_fallback_required",
]

DEFAULT_MAX_OPS = 32
DEFAULT_MAX_BYTES = 65_536

_FALLBACK_CODES = frozenset(
    {
        HED_PATCH_0001,
        HED_PATCH_0002,
        HED_PATCH_0003,
        HED_PATCH_0004,
    }
)


def _is_number(value: object) -> TypeGuard[int | float]:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_object_mapping(value: object) -> TypeGuard[Mapping[object, object]]:
    return isinstance(value, Mapping)


def _is_object_sequence(value: object) -> TypeGuard[Sequence[object]]:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes))


def _is_mutable_string_mapping(
    value: object,
) -> TypeGuard[MutableMapping[str, object]]:
    if not isinstance(value, MutableMapping):
        return False
    mapping = cast(MutableMapping[object, object], value)
    return all(isinstance(key, str) for key in mapping)


class PatchOp(StrEnum):
    ASSIGN = "assign"
    MERGE = "merge"
    APPEND = "append"
    PREPEND = "prepend"
    EXTEND = "extend"
    INSERT = "insert"
    REMOVE = "remove"
    DELETE = "delete"
    CLEAR = "clear"
    REORDER = "reorder"
    REVERSE = "reverse"
    INCREMENT = "increment"
    DECREMENT = "decrement"
    CLAMP = "clamp"


CollectionSelectorKind = Literal[
    "map",
    "gather",
    "broadcast",
    "exact_member",
    "ordered_range",
]


class PatchError(ValueError):
    """Property or collection patch failed closed."""

    def __init__(
        self,
        message: str,
        *,
        code: str = HED_PATCH_0004,
        diagnostic: HedronError | None = None,
        fallback: bool = True,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.diagnostic = diagnostic
        self.fallback = fallback


@dataclass(frozen=True, slots=True)
class PropertyPatch:
    """Single bounded mutation against a declared target property path."""

    target_id: str
    path: str
    op: PatchOp | str
    value: object | None = None
    expected_version: int | None = None


@dataclass(frozen=True, slots=True)
class CollectionSelector:
    """Typed selector for structured collection identities."""

    kind: CollectionSelectorKind
    key: str | None = None
    start: int | None = None
    stop: int | None = None
    member_id: str | None = None


@dataclass(frozen=True, slots=True)
class CollectionPatch:
    """Bounded mutation against members of a structured collection."""

    collection_id: str
    selector: CollectionSelector | str
    op: PatchOp | str
    value: object | None = None
    path: str = ""
    expected_version: int | None = None
    member_patches: tuple[PropertyPatch, ...] = ()


def full_fragment_fallback_required(exc: BaseException) -> bool:
    """Return True when ``exc`` requires a full-fragment region refresh."""
    if isinstance(exc, PatchError):
        return bool(exc.fallback) or exc.code in _FALLBACK_CODES
    return False


def apply_property_patch(
    state: Mapping[str, object],
    patch: PropertyPatch,
    *,
    max_ops: int = DEFAULT_MAX_OPS,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> dict[str, object]:
    """Apply ``patch`` to ``state``, returning a new state mapping.

    ``state`` is keyed by target id. Each target entry is a mapping that may include an
    integer ``_version`` field used for precondition checks. Caps bound operation count
    (path segments + nested merge keys) and serialized patch payload size.
    """
    if max_ops < 1:
        raise _patch_error(
            HED_PATCH_0001,
            "max_ops must be >= 1.",
            title="Invalid patch budget",
            remediation="Pass a positive max_ops cap.",
        )
    if max_bytes < 1:
        raise _patch_error(
            HED_PATCH_0001,
            "max_bytes must be >= 1.",
            title="Invalid patch budget",
            remediation="Pass a positive max_bytes cap.",
        )

    op = _coerce_op(patch.op)
    payload_bytes = _payload_size(patch.value)
    if payload_bytes > max_bytes:
        raise _patch_error(
            HED_PATCH_0003,
            f"Patch payload ({payload_bytes} bytes) exceeds max_bytes={max_bytes}.",
            title="Patch payload too large",
            remediation="Reduce the patch value or raise the declared payload cap.",
        )

    segments = _path_segments(patch.path)
    op_cost = 1 + len(segments)
    if op is PatchOp.MERGE and _is_object_mapping(patch.value):
        op_cost += len(patch.value)
    if op_cost > max_ops:
        raise _patch_error(
            HED_PATCH_0003,
            f"Patch operation cost ({op_cost}) exceeds max_ops={max_ops}.",
            title="Patch operation budget exceeded",
            remediation="Shorten the path or split the merge into smaller patches.",
        )

    if patch.target_id not in state:
        raise _patch_error(
            HED_PATCH_0001,
            f"Unknown patch target {patch.target_id!r}.",
            title="Undeclared patch target",
            remediation="Only declared targets may receive PropertyPatch updates.",
        )

    current = state[patch.target_id]
    if not is_string_mapping(current):
        raise _patch_error(
            HED_PATCH_0001,
            f"Target {patch.target_id!r} state must be a mapping.",
            title="Invalid target state",
            remediation="Store target state as a dict-like mapping.",
        )

    if patch.expected_version is not None:
        actual = current.get("_version")
        if actual != patch.expected_version:
            raise _patch_error(
                HED_PATCH_0002,
                (
                    f"Version mismatch for {patch.target_id!r}: "
                    f"expected {patch.expected_version!r}, got {actual!r}."
                ),
                title="Patch version mismatch",
                remediation="Refresh the region and retry with the current version.",
            )

    new_target: dict[str, object] = copy.deepcopy(dict(current))
    try:
        _apply_op(new_target, segments, op, patch.value)
    except PatchError:
        raise
    except Exception as exc:
        raise _patch_error(
            HED_PATCH_0004,
            f"Failed to apply {op.value} at {patch.path!r}: {exc}",
            title="Patch apply failure",
            remediation="Correct the path/op or fall back to a full fragment.",
        ) from exc

    result: dict[str, object] = {
        key: (copy.deepcopy(value) if key != patch.target_id else new_target)
        for key, value in state.items()
    }
    result[patch.target_id] = new_target
    return result


def _coerce_op(op: PatchOp | str) -> PatchOp:
    try:
        return op if isinstance(op, PatchOp) else PatchOp(op)
    except ValueError as exc:
        raise _patch_error(
            HED_PATCH_0001,
            f"Unknown patch op {op!r}.",
            title="Invalid patch operation",
            remediation=f"Use one of: {', '.join(o.value for o in PatchOp)}.",
        ) from exc


def _path_segments(path: str) -> list[str]:
    if path in {"", ".", "/"}:
        return []
    cleaned = path.replace("/", ".").strip(".")
    if not cleaned:
        return []
    return [part for part in cleaned.split(".") if part]


def _payload_size(value: object) -> int:
    try:
        return len(json.dumps(value, default=str, separators=(",", ":")).encode("utf-8"))
    except (TypeError, ValueError):
        return len(repr(value).encode("utf-8"))


def _apply_op(
    root: MutableMapping[str, object],
    segments: Sequence[str],
    op: PatchOp,
    value: object | None,
) -> None:
    if not segments:
        parent: MutableMapping[str, object] | list[object] = root
        key: str | int | None = None
    else:
        parent, key, _current = _resolve_parent(root, segments)

    if op is PatchOp.ASSIGN:
        _set_at(parent, key, value)
        return
    if op is PatchOp.MERGE:
        _op_merge(parent, key, value)
        return
    if op is PatchOp.APPEND:
        _op_append(parent, key, value)
        return
    if op is PatchOp.PREPEND:
        _op_prepend(parent, key, value)
        return
    if op is PatchOp.EXTEND:
        _op_extend(parent, key, value)
        return
    if op is PatchOp.INSERT:
        _op_insert(parent, key, value)
        return
    if op is PatchOp.REMOVE:
        _op_remove(parent, key, value)
        return
    if op is PatchOp.DELETE:
        _op_delete(parent, key)
        return
    if op is PatchOp.CLEAR:
        _op_clear(parent, key)
        return
    if op is PatchOp.REORDER:
        _op_reorder(parent, key, value)
        return
    if op is PatchOp.REVERSE:
        _op_reverse(parent, key)
        return
    if op is PatchOp.INCREMENT:
        _op_increment(parent, key, value)
        return
    if op is PatchOp.DECREMENT:
        _op_decrement(parent, key, value)
        return
    if op is PatchOp.CLAMP:
        _op_clamp(parent, key, value)
        return
    raise _patch_error(
        HED_PATCH_0001,
        f"Unsupported patch op {op!r}.",
        title="Unsupported patch operation",
        remediation="Use a documented PatchOp value.",
    )


def _op_merge(
    parent: MutableMapping[str, object] | list[object],
    key: str | int | None,
    value: object | None,
) -> None:
    if not _is_object_mapping(value):
        raise _patch_error(
            HED_PATCH_0001,
            "merge requires a mapping value.",
            title="Invalid merge patch",
            remediation="Pass a dict-like value for merge.",
        )
    target = _get_at(parent, key) if key is not None else parent
    created = target is None
    if target is None:
        target = _empty_patch_mapping()
    if not _is_mutable_string_mapping(target):
        raise _patch_error(
            HED_PATCH_0001,
            "merge target must be a mapping.",
            title="Invalid merge target",
            remediation="Merge only into object properties.",
        )
    for mk, mv in value.items():
        target[str(mk)] = copy.deepcopy(mv)
    if created:
        _set_at(parent, key, target)


def _op_append(
    parent: MutableMapping[str, object] | list[object],
    key: str | int | None,
    value: object | None,
) -> None:
    seq = _require_list(parent, key, create=True)
    seq.append(copy.deepcopy(value))


def _op_prepend(
    parent: MutableMapping[str, object] | list[object],
    key: str | int | None,
    value: object | None,
) -> None:
    seq = _require_list(parent, key, create=True)
    seq.insert(0, copy.deepcopy(value))


def _op_extend(
    parent: MutableMapping[str, object] | list[object],
    key: str | int | None,
    value: object | None,
) -> None:
    if not _is_object_sequence(value):
        raise _patch_error(
            HED_PATCH_0001,
            "extend requires a sequence value.",
            title="Invalid extend patch",
            remediation="Pass a list/tuple of items to extend.",
        )
    seq = _require_list(parent, key, create=True)
    seq.extend(copy.deepcopy(list(value)))


def _op_insert(
    parent: MutableMapping[str, object] | list[object],
    key: str | int | None,
    value: object | None,
) -> None:
    if not is_string_mapping(value) or "index" not in value or "item" not in value:
        raise _patch_error(
            HED_PATCH_0001,
            "insert requires {'index': int, 'item': ...}.",
            title="Invalid insert patch",
            remediation="Provide index and item for insert.",
        )
    seq = _require_list(parent, key, create=True)
    index = value["index"]
    if not isinstance(index, int) or isinstance(index, bool):
        raise _patch_error(
            HED_PATCH_0001,
            "insert index must be an integer.",
            title="Invalid insert patch",
            remediation="Provide an integer index for insert.",
        )
    seq.insert(index, copy.deepcopy(value["item"]))


def _op_remove(
    parent: MutableMapping[str, object] | list[object],
    key: str | int | None,
    value: object | None,
) -> None:
    seq = _require_list(parent, key, create=False)
    if value not in seq:
        raise _patch_error(
            HED_PATCH_0004,
            "remove target is not present in the sequence.",
            title="Patch remove missed",
            remediation="Refresh the fragment; do not assume a missing member was removed.",
        )
    seq.remove(value)


def _op_delete(
    parent: MutableMapping[str, object] | list[object],
    key: str | int | None,
) -> None:
    if key is None:
        raise _patch_error(
            HED_PATCH_0001,
            "delete requires a non-empty path.",
            title="Invalid delete patch",
            remediation="Provide a property path to delete.",
        )
    if isinstance(parent, list):
        if isinstance(key, int) and 0 <= key < len(parent):
            del parent[key]
            return
    else:
        if str(key) not in parent:
            raise _patch_error(
                HED_PATCH_0004,
                "delete target key is not present.",
                title="Patch delete missed",
                remediation="Refresh the fragment; do not assume a missing key was deleted.",
            )
        parent.pop(str(key))
        return
    raise _patch_error(
        HED_PATCH_0004,
        "delete target is not present.",
        title="Patch delete missed",
        remediation="Refresh the fragment; do not assume a missing member was deleted.",
    )


def _op_clear(
    parent: MutableMapping[str, object] | list[object],
    key: str | int | None,
) -> None:
    target = _get_at(parent, key) if key is not None else parent
    if is_object_list(target) or _is_mutable_string_mapping(target):
        target.clear()
    else:
        _set_at(parent, key, {})


def _op_reorder(
    parent: MutableMapping[str, object] | list[object],
    key: str | int | None,
    value: object | None,
) -> None:
    seq = _require_list(parent, key, create=False)
    if not _is_object_sequence(value):
        raise _patch_error(
            HED_PATCH_0001,
            "reorder requires a sequence of indices.",
            title="Invalid reorder patch",
            remediation="Pass the new index order as a list of ints.",
        )
    if not all(isinstance(item, int) and not isinstance(item, bool) for item in value):
        raise _patch_error(
            HED_PATCH_0001,
            "reorder indices must be integers.",
            title="Invalid reorder indices",
            remediation="Provide each integer index exactly once.",
        )
    indices = [item for item in value if isinstance(item, int) and not isinstance(item, bool)]
    if sorted(indices) != list(range(len(seq))):
        raise _patch_error(
            HED_PATCH_0001,
            "reorder indices must be a permutation of the list.",
            title="Invalid reorder indices",
            remediation="Provide each index exactly once.",
        )
    reordered = [seq[i] for i in indices]
    seq[:] = reordered


def _op_reverse(
    parent: MutableMapping[str, object] | list[object],
    key: str | int | None,
) -> None:
    seq = _require_list(parent, key, create=False)
    seq.reverse()


def _op_increment(
    parent: MutableMapping[str, object] | list[object],
    key: str | int | None,
    value: object | None,
) -> None:
    current = _get_at(parent, key)
    delta = 1 if value is None else value
    if not _is_number(current) or not _is_number(delta):
        raise _patch_error(
            HED_PATCH_0001,
            "increment requires numeric current and delta.",
            title="Invalid increment patch",
            remediation="Target a numeric property.",
        )
    _set_at(parent, key, current + delta)


def _op_decrement(
    parent: MutableMapping[str, object] | list[object],
    key: str | int | None,
    value: object | None,
) -> None:
    current = _get_at(parent, key)
    delta = 1 if value is None else value
    if not _is_number(current) or not _is_number(delta):
        raise _patch_error(
            HED_PATCH_0001,
            "decrement requires numeric current and delta.",
            title="Invalid decrement patch",
            remediation="Target a numeric property.",
        )
    _set_at(parent, key, current - delta)


def _op_clamp(
    parent: MutableMapping[str, object] | list[object],
    key: str | int | None,
    value: object | None,
) -> None:
    current = _get_at(parent, key)
    if not _is_number(current):
        raise _patch_error(
            HED_PATCH_0001,
            "clamp requires a numeric current value.",
            title="Invalid clamp patch",
            remediation="Target a numeric property.",
        )
    if not is_string_mapping(value):
        raise _patch_error(
            HED_PATCH_0001,
            "clamp requires {'min': ..., 'max': ...}.",
            title="Invalid clamp bounds",
            remediation="Pass min/max bounds as a mapping.",
        )
    lo = value.get("min")
    hi = value.get("max")
    if (lo is not None and not _is_number(lo)) or (hi is not None and not _is_number(hi)):
        raise _patch_error(
            HED_PATCH_0001,
            "clamp min/max must be numeric.",
            title="Invalid clamp bounds",
            remediation="Pass numeric min and max.",
        )
    clamped = max(current, lo) if _is_number(lo) else current
    clamped = min(clamped, hi) if _is_number(hi) else clamped
    _set_at(parent, key, clamped)


def _resolve_parent(
    root: MutableMapping[str, object],
    segments: Sequence[str],
) -> tuple[MutableMapping[str, object] | list[object], str | int, object]:
    cursor: object = root
    for part in segments[:-1]:
        if _is_mutable_string_mapping(cursor):
            nxt = cursor.get(part)
            if nxt is None:
                nxt = _empty_patch_mapping()
                cursor[part] = nxt
            cursor = nxt
        elif is_object_list(cursor):
            idx = int(part)
            cursor = cursor[idx]
        else:
            raise _patch_error(
                HED_PATCH_0001,
                f"Cannot traverse into non-container at {part!r}.",
                title="Invalid patch path",
                remediation="Use a path that resolves through mappings/lists.",
            )
    last = segments[-1]
    if _is_mutable_string_mapping(cursor):
        return cursor, last, cursor.get(last)
    if is_object_list(cursor):
        idx = int(last)
        return cursor, idx, cursor[idx] if 0 <= idx < len(cursor) else None
    raise _patch_error(
        HED_PATCH_0001,
        "Patch path parent must be a mapping or list.",
        title="Invalid patch path",
        remediation="Use a path that resolves through mappings/lists.",
    )


def _get_at(
    parent: MutableMapping[str, object] | list[object],
    key: str | int | None,
) -> object | None:
    if key is None:
        return parent
    if isinstance(parent, list):
        return parent[key] if isinstance(key, int) and 0 <= key < len(parent) else None
    return parent.get(str(key))


def _set_at(
    parent: MutableMapping[str, object] | list[object],
    key: str | int | None,
    value: object,
) -> None:
    if key is None:
        if not isinstance(parent, list) and is_string_mapping(value):
            parent.clear()
            parent.update(copy.deepcopy(dict(value)))
            return
        raise _patch_error(
            HED_PATCH_0001,
            "Cannot replace root with a non-mapping value.",
            title="Invalid root assign",
            remediation="Assign nested paths or provide a mapping for the root.",
        )
    if isinstance(parent, list):
        if isinstance(key, int):
            while len(parent) <= key:
                parent.append(None)
            parent[key] = copy.deepcopy(value)
            return
    else:
        parent[str(key)] = copy.deepcopy(value)
        return
    raise _patch_error(
        HED_PATCH_0001,
        "Cannot set value at path.",
        title="Invalid patch path",
        remediation="Use a path that resolves through mappings/lists.",
    )


def _require_list(
    parent: MutableMapping[str, object] | list[object],
    key: str | int | None,
    *,
    create: bool,
) -> list[object]:
    current = _get_at(parent, key) if key is not None else parent
    if current is None and create and key is not None:
        created: list[object] = []
        _set_at(parent, key, created)
        return created
    if not is_object_list(current):
        raise _patch_error(
            HED_PATCH_0001,
            "List operation requires a list target.",
            title="Invalid list patch target",
            remediation="Target a list property for append/prepend/extend/insert.",
        )
    return current


def _empty_patch_mapping() -> dict[str, object]:
    return {}


def _patch_error(
    code: str,
    message: str,
    *,
    title: str,
    remediation: str,
) -> PatchError:
    diagnostic = error(
        code,
        title=title,
        explanation=message,
        remediation=remediation,
    )
    return PatchError(message, code=code, diagnostic=diagnostic, fallback=True)
