"""Explicit test-suite opt-in to Hedron's optional browser-testing plugins."""

from importlib.util import find_spec

pytest_plugins = ["hedron.testing.pytest_plugin"]
if find_spec("hedron_sample_kit") is not None:
    pytest_plugins.append("hedron_sample_kit.pytest_plugin")
