"""Negative fixture: a local interaction may not carry a request lane."""

from hedron_core.interaction_067 import Interaction, LocalEffect, RequestEffect

Interaction(
    "local",
    local_effect=LocalEffect("toggle", ("open",), {"open": False}),
    request_effect=RequestEffect("status"),
)
