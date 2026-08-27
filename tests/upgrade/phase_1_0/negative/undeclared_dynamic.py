"""Negative fixture: dynamic reflection is never auto-rewritten."""

getattr(app, "refreshable")("/status")  # noqa: B009,F821
