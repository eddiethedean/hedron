"""Render-tree construction for interaction results and OOB envelopes."""

from __future__ import annotations

from hedron_core.component import NodeLike
from hedron_core.htmx.authorize import authorize_oob_update
from hedron_core.htmx.oob import (
    bound_oob_element_id,
    conflicting_select_oob_targets,
    unparsed_select_oob_tokens,
)
from hedron_core.htmx.policy import (
    OOB_ENVELOPE_TAGS,
    InteractionResult,
    OobEnvelopeTag,
)
from hedron_core.htmx_contract import safe_hx_swap


def oob_swap(
    element_id: str,
    content: NodeLike,
    *,
    swap: str = "innerHTML",
    tag: OobEnvelopeTag = "div",
) -> NodeLike:
    """Mark a node for HTMX out-of-band swap via hx-swap-oob (framework-neutral)."""
    if not element_id.replace("-", "").replace("_", "").isalnum():
        raise ValueError("Unsafe OOB element id")
    if tag not in OOB_ENVELOPE_TAGS:
        raise ValueError(
            f"Unsupported OOB envelope tag={tag!r}; allowlisted: {sorted(OOB_ENVELOPE_TAGS)}"
        )
    if not safe_hx_swap(swap):
        raise ValueError(f"Unsafe OOB swap value: {swap!r}")
    from hedron_core.html import html

    return getattr(html, tag)(content, id=element_id, **{"hx-swap-oob": swap})


def materialize_interaction_nodes(
    result: InteractionResult,
    *,
    select_oob: str | None = None,
) -> NodeLike | None:
    """Authorize OOB updates and return a renderable node tree (or None).

    When ``select_oob`` (or ``result.select_oob``) is known, fail closed on
    same-target ``hx-select-oob`` / ``OobUpdate`` collisions and on non-``#id``
    select-oob tokens.
    """
    from hedron_core.builtins import Fragment

    effective_select_oob = select_oob if select_oob is not None else result.select_oob
    if effective_select_oob:
        unparsed = unparsed_select_oob_tokens(effective_select_oob)
        if unparsed:
            tokens = ", ".join(sorted(unparsed))
            raise ValueError(
                f"select_oob must use simple #id selectors only; unsupported token(s): {tokens}"
            )
        conflicts = conflicting_select_oob_targets(effective_select_oob, result.oob)
        if conflicts:
            targets = ", ".join(f"#{item}" for item in sorted(conflicts))
            raise ValueError(
                f"select_oob / OobUpdate same-target conflict for {targets}; "
                "use one OOB mechanism per target (prefer OobUpdate with "
                "swap='innerHTML' and omit matching select_oob)"
            )

    regions = result.policy.declared_regions if result.policy is not None else ()
    if not result.oob:
        return result.content
    nodes: list[NodeLike] = []
    if result.content is not None:
        nodes.append(result.content)
    seen_oob_ids: set[str] = set()
    for update in result.oob:
        authorize_oob_update(update, regions=regions)
        bound_id = bound_oob_element_id(update, regions=regions)
        if bound_id is not None and bound_id in seen_oob_ids:
            raise ValueError(f"duplicate OobUpdate element_id: {bound_id!r}")
        if bound_id is not None:
            seen_oob_ids.add(bound_id)
        if bound_id is not None:
            # Always wrap to the authorized id so caller content cannot emit a
            # different hx-swap-oob target under declared regions.
            node: NodeLike = oob_swap(
                bound_id,
                update.content,
                swap=update.swap,
                tag=update.tag,
            )
        else:
            node = update.content
        nodes.append(node)
    if not nodes:
        return None
    if len(nodes) == 1:
        return nodes[0]
    return Fragment(*nodes)
