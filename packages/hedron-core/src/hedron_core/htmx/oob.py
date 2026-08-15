"""hx-select-oob parsing and same-target conflict detection."""

from __future__ import annotations

from collections.abc import Sequence

from hedron_core.htmx.policy import FragmentRegion, OobUpdate
from hedron_core.htmx_contract import safe_css_selector


def parse_select_oob_element_ids(select_oob: str | None) -> frozenset[str]:
    """Extract simple ``#id`` targets from an ``hx-select-oob`` value.

    Only ``#id`` tokens (alphanumeric / ``_`` / ``-``) are recognized. Complex
    selectors are ignored for conflict detection; use
    :func:`unparsed_select_oob_tokens` to surface them.
    """
    if not select_oob:
        return frozenset()
    ids: set[str] = set()
    for part in select_oob.split(","):
        token = part.strip()
        if not token or not safe_css_selector(token) or not token.startswith("#"):
            continue
        element_id = token[1:]
        if element_id.replace("-", "").replace("_", "").isalnum():
            ids.add(element_id)
    return frozenset(ids)


def unparsed_select_oob_tokens(select_oob: str | None) -> frozenset[str]:
    """Return ``hx-select-oob`` tokens that are not simple ``#id`` selectors.

    Hedron's conflict scanner only understands ``#id`` lists. Attribute or
    descendant selectors are returned here so hosts can warn or document the
    limitation.
    """
    if not select_oob:
        return frozenset()
    unparsed: set[str] = set()
    for part in select_oob.split(","):
        token = part.strip()
        if not token:
            continue
        if not safe_css_selector(token) or not token.startswith("#"):
            unparsed.add(token)
            continue
        element_id = token[1:]
        if not element_id.replace("-", "").replace("_", "").isalnum():
            unparsed.add(token)
    return frozenset(unparsed)


def oob_update_element_ids(oob: Sequence[OobUpdate] | None) -> frozenset[str]:
    """Return element ids that ``OobUpdate`` values will bind for ``hx-swap-oob``."""
    if not oob:
        return frozenset()
    ids: set[str] = set()
    for update in oob:
        bound = bound_oob_element_id(update, regions=())
        if bound is not None:
            ids.add(bound)
    return frozenset(ids)


def conflicting_select_oob_targets(
    select_oob: str | None,
    oob: Sequence[OobUpdate] | None = None,
    *,
    oob_ids: frozenset[str] | set[str] | None = None,
) -> frozenset[str]:
    """Return ids targeted by both ``hx-select-oob`` and server ``OobUpdate``.

    Use one mechanism per target. Prefer explicit ``OobUpdate`` (omit matching
    ``select_oob``) so ``innerHTML`` swaps preserve semantic shell hosts.
    """
    selected = parse_select_oob_element_ids(select_oob)
    if not selected:
        return frozenset()
    bound = frozenset(oob_ids) if oob_ids is not None else oob_update_element_ids(oob)
    return frozenset(selected & bound)


def bound_oob_element_id(
    update: OobUpdate,
    *,
    regions: tuple[FragmentRegion, ...] = (),
) -> str | None:
    del regions  # regions authorize; id binding uses element_id / #select.
    if update.element_id is not None:
        return update.element_id
    if update.select and update.select.startswith("#"):
        return update.select[1:]
    return None
