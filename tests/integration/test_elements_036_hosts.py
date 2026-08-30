"""ELEMENTS-036: host registration / render smoke (FastAPI + adapters)."""

from __future__ import annotations

from hedron_core.plugins import PluginContext
from hedron_core.registry import get_registry, reset_registry_for_tests
from hedron_core.rendering import render
from hedron_elements.example import Example
from hedron_elements.plugin import PLUGIN_META, register


def setup_function() -> None:
    reset_registry_for_tests()


def teardown_function() -> None:
    reset_registry_for_tests()


def test_plugin_registers_element_and_component() -> None:
    class _Ctx(PluginContext):
        def __init__(self) -> None:
            super().__init__(PLUGIN_META)

        def register_diagnostic_owner(self, prefix: str) -> None:
            self.prefix = prefix

        def register_feature(self, **kwargs: object) -> None:
            self.feature = kwargs

        def register_explorer_panel(self, **kwargs: object) -> None:
            return None

        def register_projection_provider(self, provider: object) -> None:
            return None

    ctx = _Ctx()
    register(ctx)
    reg = get_registry()
    assert any(m.tag_name == "hedron-example" for m in reg.browser_modules())
    assert reg.get_element_definition("hedron-example") is not None
    assert any(c.distribution == "hedron-elements" for c in reg.components())
    assert ctx.prefix == "HED-ELEMENT-"


def test_fastapi_page_render_includes_example() -> None:
    from hedron import Hedron
    from hedron_core.builtins import Page, Text

    app = Hedron(title="el", explorer="off", session_secret="secret")

    @app.page("/")
    def home() -> Page:
        return Page(Text("Hi"), Example(status="Ready"))

    html = render(home()).html
    assert "hedron-example" in html


def test_example_markup_without_full_plugin_load() -> None:
    assert "hedron-example" in Example(status="x").render_markup()
