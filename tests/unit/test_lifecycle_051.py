"""LIFECYCLE-051 shared extras host ABI."""

from __future__ import annotations

from pathlib import Path

from hedron.testing import assert_renders
from hedron_core import __version__ as core_version
from hedron_core.plugin_loader import load_plugins
from hedron_core.plugins import reset_explorer_panels_for_tests
from hedron_core.registry import get_registry, reset_registry_for_tests
from hedron_extras.composition import ChoiceCards
from hedron_extras.descriptor import SUPPORTED_BROWSER_TAGS
from hedron_extras.plugin import register as extras_register


class _EP:
    def __init__(self, name: str = "hedron_extras") -> None:
        self.name = name

    def load(self) -> object:
        return extras_register


def setup_function() -> None:
    reset_registry_for_tests()
    reset_explorer_panels_for_tests()


def test_supported_hosts_share_lifecycle_js() -> None:
    load_plugins(enabled=["hedron_extras"], hedron_version=core_version, entry_points=[_EP()])
    modules = list(get_registry().browser_modules())
    tags = {m.tag_name for m in modules}
    assert set(SUPPORTED_BROWSER_TAGS) <= tags
    assert "hedron-extras-sandbox" not in tags
    assert "hedron-extras-code-editor" not in tags
    for module in modules:
        if module.tag_name in SUPPORTED_BROWSER_TAGS:
            assert module.htmx_lifecycle is True
            assert module.observed_attributes == ("data-hedron-payload",)
            assert module.shadow_dom is False
            assert "lifecycle/host.js" in module.module_path
    host = Path("packages/hedron-extras/src/hedron_extras/assets/lifecycle/host.js").read_text(
        encoding="utf-8"
    )
    for token in (
        "connectedCallback",
        "disconnectedCallback",
        "AbortController",
        "revokeObjectURL",
        "customElements.define",
        "htmx:afterSwap",
    ):
        assert token in host
    html = assert_renders(
        ChoiceCards("pick", [{"value": "a", "label": "A"}]),
        contains="hedron-extras-composition",
    )
    assert "data-hedron-payload" in html
