"""Authorize HTMX targets, OOB updates, and outbound selectors."""

from __future__ import annotations

import json

from hedron_core.htmx.policy import (
    FragmentRegion,
    FragmentRegionError,
    InteractionPolicy,
    OobUpdate,
)
from hedron_core.htmx_contract import safe_css_selector


def _declared_region_labels(regions: tuple[FragmentRegion, ...]) -> tuple[str, ...]:
    return tuple(f"{region.id} ({region.selector})" for region in regions)


def _single_hash_id(value: str) -> str | None:
    """Return the id after at most one leading ``#``, or None if malformed.

    Rejects ``##panel`` / ``###panel`` (``str.lstrip('#')`` would collapse them).
    """
    if value.startswith("##"):
        return None
    return value.removeprefix("#")


def resolve_fragment_region(
    policy: InteractionPolicy | None,
    target: str | None,
) -> FragmentRegion | None:
    """Resolve ``target`` against declared regions by ``selector`` match.

    Authorization is selector-based (``FragmentRegion.id`` is bookkeeping only).
    Accepts either the exact declared selector (``#panel``) or HTMX's common bare-id
    header form (``panel``) when the selector is a single ``#id``. Rejects
    ``##…`` collapsing and matching on ``region.id`` when it differs from the
    selector id.
    """
    if policy is None or not policy.declared_regions:
        return None
    if target is None:
        # Fail closed: do not implicitly authorize the first declared region.
        # authorize_htmx_target already rejects missing HX-Target when regions exist.
        return None
    if target.startswith("##"):
        declared = _declared_region_labels(policy.declared_regions)
        raise FragmentRegionError(
            f"HX-Target {target!r} is not an authorized fragment region for this route",
            requested=target,
            declared=declared,
        )
    for region in policy.declared_regions:
        if region.selector == target:
            return region
        # HTMX frequently sends HX-Target without the leading '#' for #id selectors.
        if (
            region.selector.startswith("#")
            and not region.selector.startswith("##")
            and "#" not in region.selector[1:]
            and target == region.selector[1:]
        ):
            return region
    declared = _declared_region_labels(policy.declared_regions)
    raise FragmentRegionError(
        f"HX-Target {target!r} is not an authorized fragment region for this route",
        requested=target,
        declared=declared,
    )


def select_htmx_auth_target(
    *,
    client_target: str | None,
    region_id: str | None,
) -> str | None:
    """Choose the HTMX target used for authorization.

    Prefer the client ``HX-Target`` when present. When both client target and
    handler ``region_id`` are set but refer to different ids, reject — the
    browser swaps into ``HX-Target``, so authorizing ``region_id`` alone is
    fail-open. ``region_id`` is compared with a single leading ``#`` stripped
    (never ``lstrip``), and multi-hash targets are rejected.
    """
    if client_target and client_target.startswith("##"):
        raise FragmentRegionError(
            f"HX-Target {client_target!r} is not a valid fragment selector",
            requested=client_target,
            declared=(region_id,) if region_id else (),
        )
    if client_target and region_id:
        client_id = _single_hash_id(client_target)
        handler_id = _single_hash_id(region_id)
        if client_id is None or handler_id is None or client_id != handler_id:
            raise FragmentRegionError(
                f"HX-Target {client_target!r} disagrees with region_id {region_id!r}",
                requested=client_target,
                declared=(region_id,),
            )
        return client_target
    if client_target:
        return client_target
    if region_id is None:
        return None
    # Server bookkeeping ids are not CSS selectors; normalize to #id so
    # resolve_fragment_region can exact-match the common selector=f"#{id}" form
    # without accepting bare client HX-Target values.
    if region_id.startswith("##"):
        raise FragmentRegionError(
            f"region_id {region_id!r} is not a valid fragment selector",
            requested=region_id,
            declared=(region_id,),
        )
    return region_id if region_id.startswith("#") else f"#{region_id}"


def authorize_htmx_target(
    policy: InteractionPolicy | None,
    target: str | None,
    *,
    is_htmx: bool,
    history_restore: bool = False,
) -> FragmentRegion | None:
    """Authorize ``HX-Target`` for HTMX requests (fail closed by default).

    When the client sends ``HX-Target`` and no ``declared_regions`` are present,
    raise :class:`FragmentRegionError` unless ``allow_undeclared_targets`` is set.
    HTMX fragment requests with declared regions but a missing ``HX-Target`` also fail
    closed (do not implicitly authorize the first region). History-restore requests
    may omit ``HX-Target`` and still succeed (full PAGE navigation restore).
    """
    regions = policy.declared_regions if policy is not None else ()
    allow_open = bool(policy is not None and policy.allow_undeclared_targets)
    if is_htmx and target and not regions and not allow_open:
        raise FragmentRegionError(
            "HX-Target requires declared fragment_regions on this route "
            "(set InteractionPolicy.allow_undeclared_targets=True to opt out)",
            requested=target,
            declared=(),
        )
    if is_htmx and regions and not target and not allow_open and not history_restore:
        raise FragmentRegionError(
            "HTMX requests with declared fragment_regions require HX-Target",
            requested=None,
            declared=_declared_region_labels(regions),
        )
    if not regions or target is None:
        return None
    return resolve_fragment_region(policy, target)


# Framework-owned OOB sinks that swap(toast=...) may target without declaring them on
# every fragment route. Does not weaken HX-Target authorization for primary swaps.
RESERVED_OOB_ELEMENT_IDS = frozenset({"hedron-toast"})

# Framework-owned status / chrome sinks allowed as HX-Retarget / HX-Reselect hosts
# without declaring them on every fragment route (status policies + toast).
RESERVED_RESPONSE_SINK_IDS = frozenset({"hedron-toast", "hedron-errors", "hedron-auth"})

def _is_reserved_oob_target(*, element_id: str | None, select: str | None) -> bool:
    if element_id is not None and element_id in RESERVED_OOB_ELEMENT_IDS:
        return True
    if select is not None:
        needle = _single_hash_id(select)
        if needle is not None and needle in RESERVED_OOB_ELEMENT_IDS and select == f"#{needle}":
            return True
    return False


def _is_reserved_response_sink(selector: str) -> bool:
    """True when ``selector`` is exactly ``#<reserved-id>`` (bare ids rejected)."""
    if selector.startswith("##"):
        return False
    needle = _single_hash_id(selector)
    return needle is not None and needle in RESERVED_RESPONSE_SINK_IDS and selector == f"#{needle}"


def authorize_response_selector(
    policy: InteractionPolicy | None,
    selector: str | None,
    *,
    header_name: str = "HX-Retarget",
) -> None:
    """Authorize outbound ``HX-Retarget`` / ``HX-Reselect`` against declared regions.

    Reserved framework sinks (``#hedron-toast``, ``#hedron-errors``, ``#hedron-auth``)
    are always allowed. When ``declared_regions`` are present, other selectors must
    resolve like inbound ``HX-Target``. ``allow_undeclared_targets`` opts out.
    With no declared regions there is no allowlist to enforce (selector safety still
    runs via :func:`approved_headers`).
    """
    if selector is None:
        return
    if _is_reserved_response_sink(selector):
        return
    allow_open = bool(policy is not None and policy.allow_undeclared_targets)
    if allow_open:
        return
    regions = policy.declared_regions if policy is not None else ()
    if not regions:
        return
    try:
        resolve_fragment_region(policy, selector)
    except FragmentRegionError as exc:
        declared = _declared_region_labels(regions)
        raise FragmentRegionError(
            f"{header_name} {selector!r} is not an authorized fragment region for this route",
            requested=selector,
            declared=declared,
            code=exc.code,
        ) from exc


def authorize_oob_update(
    update: OobUpdate,
    *,
    regions: tuple[FragmentRegion, ...] = (),
) -> None:
    if update.select is None and update.element_id is None:
        raise ValueError("OOB updates require element_id or select")
    reserved = _is_reserved_oob_target(element_id=update.element_id, select=update.select)
    # Fail closed: without declared regions, only reserved toast/chrome ids are allowed.
    if not regions and not reserved:
        raise ValueError(
            "OOB updates require declared fragment regions (or a reserved element id "
            f"such as {sorted(RESERVED_OOB_ELEMENT_IDS)})"
        )
    if update.select is not None:
        if not safe_css_selector(update.select):
            raise ValueError("Unsafe OOB select selector")
        if regions and not reserved:
            resolve_fragment_region(
                InteractionPolicy(declared_regions=regions),
                update.select,
            )
            # With declared regions, select must resolve to a concrete #id so
            # materialize can bind the rendered OOB target to that id.
            if update.element_id is None and not update.select.startswith("#"):
                raise ValueError(
                    "OOB select without element_id must be a #id when fragment regions are declared"
                )
    if update.element_id is not None:
        if not update.element_id.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Unsafe OOB element id")
        if regions and not reserved:
            resolve_fragment_region(
                InteractionPolicy(declared_regions=regions),
                f"#{update.element_id}",
            )
        if update.select is not None and update.select.startswith("#"):
            selected_id = update.select[1:]
            if selected_id != update.element_id:
                raise ValueError("OOB element_id must match authorized select #id")

def authorize_location_selectors(
    policy: InteractionPolicy | None,
    location_header: str | None,
) -> None:
    """Authorize ``target`` / ``select`` inside an ``HX-Location`` JSON payload.

    String locations are path-only and have no selectors. Mapping payloads may
    include ``target`` / ``select`` which must pass the same region allowlist as
    ``HX-Retarget`` / ``HX-Reselect``.
    """
    if location_header is None:
        return
    text = location_header.strip()
    if not text or text[0] != "{":
        return
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("HX-Location must be a local path or JSON object") from exc
    if not isinstance(payload, dict):
        raise ValueError("HX-Location JSON must be an object")
    target = payload.get("target")
    if target is not None:
        if not isinstance(target, str):
            raise ValueError("HX-Location target must be a string selector")
        authorize_response_selector(policy, target, header_name="HX-Location target")
    select = payload.get("select")
    if select is not None:
        if not isinstance(select, str):
            raise ValueError("HX-Location select must be a string selector")
        authorize_response_selector(policy, select, header_name="HX-Location select")


