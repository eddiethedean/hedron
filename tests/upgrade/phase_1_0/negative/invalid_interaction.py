"""Negative fixture: a local interaction may not carry a request lane."""

from hedron_core.interaction_067 import Interaction, LocalEffect, RequestEffect

Interaction(
    "local",
    local_effect=LocalEffect("toggle"),
    request_effect=RequestEffect("status"),
)
