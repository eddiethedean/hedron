"""Re-export portable interaction types from hedron-core."""

from __future__ import annotations

from hedron_core.interaction import (
    FragmentRegion as FragmentRegion,
)
from hedron_core.interaction import (
    FragmentRegionError as FragmentRegionError,
)
from hedron_core.interaction import (
    HtmxRequestFacts as HtmxRequestFacts,
)
from hedron_core.interaction import (
    InteractionPolicy as InteractionPolicy,
)
from hedron_core.interaction import (
    InteractionResult as InteractionResult,
)
from hedron_core.interaction import (
    OobUpdate as OobUpdate,
)
from hedron_core.interaction import (
    StatusPolicy as StatusPolicy,
)
from hedron_core.interaction import (
    authorize_oob_update as authorize_oob_update,
)
from hedron_core.interaction import (
    conflicting_select_oob_targets as conflicting_select_oob_targets,
)
from hedron_core.interaction import (
    default_interaction_policy as default_interaction_policy,
)
from hedron_core.interaction import (
    form_sync_attrs as form_sync_attrs,
)
from hedron_core.interaction import (
    interaction_headers as portable_interaction_headers,
)
from hedron_core.interaction import (
    interaction_trace as interaction_trace,
)
from hedron_core.interaction import (
    merge_route_regions as merge_route_regions,
)
from hedron_core.interaction import (
    oob_update_element_ids as oob_update_element_ids,
)
from hedron_core.interaction import (
    parse_select_oob_element_ids as parse_select_oob_element_ids,
)
from hedron_core.interaction import (
    resolve_fragment_region as resolve_fragment_region,
)
from hedron_core.interaction import (
    status_policy_for as status_policy_for,
)

__all__ = [
    "FragmentRegion",
    "FragmentRegionError",
    "HtmxRequestFacts",
    "InteractionPolicy",
    "InteractionResult",
    "OobUpdate",
    "StatusPolicy",
    "authorize_oob_update",
    "conflicting_select_oob_targets",
    "default_interaction_policy",
    "form_sync_attrs",
    "interaction_trace",
    "merge_route_regions",
    "oob_update_element_ids",
    "parse_select_oob_element_ids",
    "portable_interaction_headers",
    "resolve_fragment_region",
    "status_policy_for",
]
