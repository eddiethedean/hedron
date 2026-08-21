"""DX-058 evidence."""

from __future__ import annotations

from hedron.cli.parser import _build_parser
from hedron.cli.scaffold import fastapi as fastapi_scaffold


def test_scaffold_templates_exist() -> None:
    assert callable(fastapi_scaffold._app_minimal)
    assert callable(fastapi_scaffold._app_crud)
    assert callable(fastapi_scaffold._app_dashboard)
    assert callable(fastapi_scaffold._app_task)
    templates = fastapi_scaffold._TEMPLATES
    assert set(templates) == {"minimal", "crud", "dashboard", "task"}
    for _name, (factory, _deps) in templates.items():
        source = factory()
        assert isinstance(source, str)
        assert "Hedron" in source


def test_template_cli_choices() -> None:
    parser = _build_parser()
    choices = None
    for action in parser._actions:
        subparsers = getattr(action, "choices", None)
        if isinstance(subparsers, dict) and "new" in subparsers:
            for sub_action in subparsers["new"]._actions:
                if "--template" in getattr(sub_action, "option_strings", ()):
                    choices = set(sub_action.choices or ())
                    break
        if "--template" in getattr(action, "option_strings", ()):
            choices = set(action.choices or ())
        if choices is not None:
            break
    assert choices == {"minimal", "crud", "dashboard", "task"}
