"""Negative fixture: a local interaction may not carry a request lane."""

Interaction.local("toggle", request_effect=RequestEffect("status"))
