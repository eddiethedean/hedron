"""Typed FastAPI/HTMX interaction envelope (adapter over portable core types)."""

from __future__ import annotations

from hedron.interaction._core import (
    FragmentRegion as FragmentRegion,
)
from hedron.interaction._core import (
    FragmentRegionError as FragmentRegionError,
)
from hedron.interaction._core import (
    InteractionPolicy as InteractionPolicy,
)
from hedron.interaction._core import (
    InteractionResult as InteractionResult,
)
from hedron.interaction._core import (
    OobUpdate as OobUpdate,
)
from hedron.interaction._core import (
    StatusPolicy as StatusPolicy,
)
from hedron.interaction._core import (
    authorize_oob_update as authorize_oob_update,
)
from hedron.interaction._core import (
    conflicting_select_oob_targets as conflicting_select_oob_targets,
)
from hedron.interaction._core import (
    default_interaction_policy as default_interaction_policy,
)
from hedron.interaction._core import (
    form_sync_attrs as form_sync_attrs,
)
from hedron.interaction._core import (
    merge_route_regions as merge_route_regions,
)
from hedron.interaction._core import (
    oob_update_element_ids as oob_update_element_ids,
)
from hedron.interaction._core import (
    parse_select_oob_element_ids as parse_select_oob_element_ids,
)
from hedron.interaction._core import (
    resolve_fragment_region as resolve_fragment_region,
)
from hedron.interaction._core import (
    status_policy_for as status_policy_for,
)
from hedron.interaction.builders import (
    redirect_htmx as redirect_htmx,
)
from hedron.interaction.builders import (
    retarget as retarget,
)
from hedron.interaction.builders import (
    swap as swap,
)
from hedron.interaction.builders import (
    swap_oob as swap_oob,
)
from hedron.interaction.headers import interaction_headers as interaction_headers
from hedron.interaction.request import HtmxRequest as HtmxRequest
from hedron.interaction.request import htmx_request as htmx_request

__all__ = [
    "FragmentRegion",
    "FragmentRegionError",
    "HtmxRequest",
    "InteractionPolicy",
    "InteractionResult",
    "OobUpdate",
    "StatusPolicy",
    "authorize_oob_update",
    "conflicting_select_oob_targets",
    "default_interaction_policy",
    "form_sync_attrs",
    "htmx_request",
    "interaction_headers",
    "merge_route_regions",
    "oob_update_element_ids",
    "parse_select_oob_element_ids",
    "redirect_htmx",
    "resolve_fragment_region",
    "retarget",
    "status_policy_for",
    "swap",
    "swap_oob",
]
