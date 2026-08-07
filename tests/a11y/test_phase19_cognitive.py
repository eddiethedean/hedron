"""Phase 0.19 COG-019."""

from __future__ import annotations

from hedron_core.a11y import CognitivePreferences


def test_cognitive_preferences_do_not_judge_prose() -> None:
    prefs = CognitivePreferences(
        reduced_motion=True,
        density="compact",
        help_slot="help",
        glossary_slot="glossary",
        simplified_presentation=True,
    )
    assert prefs.judges_prose_clarity() is False
    assert prefs.notification_intensity == "medium"
