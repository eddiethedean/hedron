"""LOWER-058 evidence."""

from __future__ import annotations

import importlib.util

from pydantic import BaseModel, Field

from hedron import ActionHandle, DesignSystem, Hedron, Page, ScreenHandle, Text
from hedron.app.screens import normalize_screen_result
from hedron_core.registry import reset_registry_for_tests


class LowerNote(BaseModel):
    message: str = Field(min_length=1, max_length=80)


def _reset() -> None:
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]


def test_screen_lowers_to_page() -> None:
    page = normalize_screen_result(Text("hello"), title="Home", layout="stack")
    assert isinstance(page, Page)
    assert page.props.title == "Home"


def test_form_command_lowers_to_action_handle() -> None:
    _reset()
    app = Hedron(
        title="t",
        security="development",
        session_secret="test-secret",
        explorer="off",
    )

    @app.form_command("/notes", fallback="/", success="Saved")
    def add_note(data: LowerNote):
        return Text(data.message)

    assert isinstance(add_note, ActionHandle)
    assert add_note.path == "/notes"


def test_design_system_to_theme() -> None:
    design = DesignSystem.brand("acme", accent="#2f6fed")
    theme = design.to_theme()
    assert theme.name == "acme"
    assert theme.palette["brand.seed"] == "#2f6fed"


def test_no_second_runtime_named_hedron_easy() -> None:
    assert importlib.util.find_spec("hedron.easy") is None
    assert isinstance(ScreenHandle, type)
