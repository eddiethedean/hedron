"""DX-058 evidence."""

from __future__ import annotations

from fastapi.testclient import TestClient

from hedron.cli.parser import _build_parser
from hedron.cli.scaffold import fastapi as fastapi_scaffold
from hedron_core import reset_registry_for_tests


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


def test_minimal_scaffold_controls_complete_fragment_and_action_requests() -> None:
    reset_registry_for_tests()
    namespace: dict[str, object] = {"__name__": "hedron_generated_minimal"}
    try:
        source = fastapi_scaffold._app_minimal()
        exec(compile(source, "generated/app.py", "exec"), namespace, namespace)
        app = namespace["app"]
        status = namespace["status"]
        ping = namespace["ping"]

        with TestClient(app, follow_redirects=False) as client:  # type: ignore[arg-type]
            page = client.get("/")
            assert page.status_code == 200
            assert f'hx-get="{status.path}"' in page.text  # type: ignore[attr-defined]
            assert f'hx-target="{status.selector}"' in page.text  # type: ignore[attr-defined]
            assert f'hx-post="{ping.path}"' in page.text  # type: ignore[attr-defined]
            assert "hx-headers" in page.text

            token = page.cookies.get("hedron_csrf")
            assert token
            fragment = client.get(
                status.path,  # type: ignore[attr-defined]
                headers={
                    "HX-Request": "true",
                    "HX-Target": status.dom_id,  # type: ignore[attr-defined]
                },
            )
            assert fragment.status_code == 200
            assert "All systems operational" in fragment.text

            action = client.post(
                ping.path,  # type: ignore[attr-defined]
                headers={"HX-Request": "true", "X-CSRF-Token": token},
            )
            assert action.status_code == 200
            assert "HX-Trigger" in action.headers

            fallback = client.post(
                ping.path,  # type: ignore[attr-defined]
                data={"csrf_token": token},
            )
            assert fallback.status_code == 303
            assert fallback.headers["location"] == "/"
    finally:
        reset_registry_for_tests()


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
