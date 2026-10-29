"""Explicit test-suite opt-in to Hedron's optional browser-testing plugins."""

pytest_plugins = [
    "hedron.testing.pytest_plugin",
    "hedron_sample_kit.pytest_plugin",
]
