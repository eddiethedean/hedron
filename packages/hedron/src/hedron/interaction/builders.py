"""InteractionResult builders for FastAPI/HTMX adapters."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from hedron.interaction._core import FragmentRegion, InteractionResult, OobUpdate
from hedron_core.component import NodeLike

__all__ = ["redirect_htmx", "retarget", "swap", "swap_oob"]


def _coerce_oob(item: OobUpdate | NodeLike) -> OobUpdate:
    if isinstance(item, OobUpdate):
        return item
    return OobUpdate(content=item)


def swap(
    content: NodeLike | None,
    *,
    toast: str | NodeLike | OobUpdate | None = None,
    oob: Sequence[OobUpdate | NodeLike] = (),
    **kwargs: Any,
) -> InteractionResult:
    """Build a primary-fragment :class:`InteractionResult` (optional toast / OOB)."""
    updates = [_coerce_oob(item) for item in oob]
    if toast is not None:
        if isinstance(toast, OobUpdate):
            updates.append(toast)
        elif isinstance(toast, str):
            from hedron_core.builtins import Toast

            updates.append(
                OobUpdate(content=Toast(toast), element_id="hedron-toast", swap="innerHTML")
            )
        else:
            updates.append(OobUpdate(content=toast, element_id="hedron-toast", swap="innerHTML"))
    return InteractionResult(content=content, oob=tuple(updates), **kwargs)


def swap_oob(
    content: NodeLike | None,
    *oob: OobUpdate | NodeLike,
    **kwargs: Any,
) -> InteractionResult:
    """Primary fragment plus one or more out-of-band updates."""
    existing = list(kwargs.pop("oob", ()) or ())
    updates = [_coerce_oob(item) for item in (*oob, *existing)]
    return InteractionResult(content=content, oob=tuple(updates), **kwargs)


def retarget(
    content: NodeLike | None,
    region: FragmentRegion | str,
    **kwargs: Any,
) -> InteractionResult:
    """Return content with an approved ``HX-Retarget`` selector."""
    if isinstance(region, FragmentRegion):
        selector = region.selector
        # Prefer the CSS selector for HX-Target agreement when id differs from selector.
        kwargs.setdefault("region_id", selector)
    else:
        selector = str(region)
    return InteractionResult(content=content, retarget=selector, **kwargs)


def redirect_htmx(url: str) -> InteractionResult:
    """Issue an HTMX ``HX-Redirect`` via :class:`InteractionResult`."""
    return InteractionResult(redirect=url)
