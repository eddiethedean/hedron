"""Negative fixture: dynamic reflection is never auto-rewritten."""

getattr(app, "refreshable")("/status")
