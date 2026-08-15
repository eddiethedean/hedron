"""Adapter-neutral interaction values and policies (framework-neutral)."""

from __future__ import annotations

from hedron_core.htmx.authorize import (
    RESERVED_OOB_ELEMENT_IDS,
    RESERVED_RESPONSE_SINK_IDS,
    authorize_htmx_target,
    authorize_location_selectors,
    authorize_oob_update,
    authorize_response_selector,
    resolve_fragment_region,
    select_htmx_auth_target,
)
from hedron_core.htmx.headers import (
    form_sync_attrs,
    interaction_headers,
    merge_interaction_headers,
    status_policy_for,
    validated_extra_headers,
)
from hedron_core.htmx.headers import (
    interaction_trace as interaction_trace,
)
from hedron_core.htmx.materialize import materialize_interaction_nodes, oob_swap
from hedron_core.htmx.oob import (
    conflicting_select_oob_targets,
    oob_update_element_ids,
    parse_select_oob_element_ids,
    unparsed_select_oob_tokens,
)
from hedron_core.htmx.policy import (
    OOB_ENVELOPE_TAGS,
    CacheHint,
    FragmentRegion,
    FragmentRegionError,
    HistoryMode,
    HtmxRequestFacts,
    InteractionPolicy,
    InteractionResult,
    OobEnvelopeTag,
    OobUpdate,
    StatusPolicy,
    apply_allow_undeclared_targets,
    default_interaction_policy,
    merge_route_regions,
)

__all__ = [
    "CacheHint",
    "FragmentRegion",
    "FragmentRegionError",
    "HistoryMode",
    "HtmxRequestFacts",
    "InteractionPolicy",
    "InteractionResult",
    "OOB_ENVELOPE_TAGS",
    "OobEnvelopeTag",
    "OobUpdate",
    "RESERVED_OOB_ELEMENT_IDS",
    "RESERVED_RESPONSE_SINK_IDS",
    "StatusPolicy",
    "authorize_htmx_target",
    "authorize_location_selectors",
    "authorize_oob_update",
    "authorize_response_selector",
    "apply_allow_undeclared_targets",
    "conflicting_select_oob_targets",
    "default_interaction_policy",
    "form_sync_attrs",
    "interaction_headers",
    "materialize_interaction_nodes",
    "merge_interaction_headers",
    "merge_route_regions",
    "oob_swap",
    "oob_update_element_ids",
    "parse_select_oob_element_ids",
    "resolve_fragment_region",
    "select_htmx_auth_target",
    "status_policy_for",
    "unparsed_select_oob_tokens",
    "validated_extra_headers",
]
