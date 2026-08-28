"""ELEMENTS-037: host registration and FastAPI render smoke."""

from __future__ import annotations

from hedron_core.plugins import PluginContext
from hedron_core.registry import get_registry, reset_registry_for_tests
from hedron_core.rendering import render
from hedron_elements.action_async import ActionAsync
from hedron_elements.dialog import Dialog
from hedron_elements.disclosure import Disclosure
from hedron_elements.example import Example
from hedron_elements.field_choice import FieldChoice
from hedron_elements.field_file import FieldFile
from hedron_elements.field_text import FieldText
from hedron_elements.plugin import PLUGIN_META, register


def setup_function() -> None:
    reset_registry_for_tests()


def teardown_function() -> None:
    reset_registry_for_tests()


def test_plugin_registers_all_037_tags() -> None:
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
    tags = {m.tag_name for m in reg.browser_modules()}
    expected = {
        "hedron-example",
        "hedron-field-text",
        "hedron-field-choice",
        "hedron-field-file",
        "hedron-disclosure",
        "hedron-dialog",
        "hedron-action-async",
    }
    assert expected <= tags
    assert ctx.prefix == "HED-ELEMENT-"


def test_fastapi_page_render_includes_037_elements() -> None:
    from hedron import Hedron
    from hedron_core.builtins import Page, Text

    app = Hedron(title="el037", explorer="off", session_secret="secret")

    @app.page("/")
    def home() -> Page:
        return Page(
            Text("Hi"),
            Example(status="Ready"),
            FieldText("email", value="a@b.c"),
            FieldChoice("opts", (("x", "X"),)),
            FieldFile(name="f"),
            Disclosure(summary="Details"),
            Dialog(title="Modal"),
            ActionAsync("Go"),
        )

    html = render(home()).html
    for tag in (
        "hedron-example",
        "hedron-field-text",
        "hedron-field-choice",
        "hedron-field-file",
        "hedron-disclosure",
        "hedron-dialog",
        "hedron-action-async",
    ):
        assert tag in html
