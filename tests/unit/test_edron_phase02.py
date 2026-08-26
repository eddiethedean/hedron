"""PHASE-EDRON-02: source-aware authoring and tooling contracts."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from starlette.testclient import TestClient

import edron as ed
from edron.diagnostics import DiagnosticReport, EdronDiagnostic, SourceLocation
from edron.scaffolds import create_scaffold
from edron.tooling import check_source


def test_diagnostic_is_structured_and_redacts_sensitive_context() -> None:
    diagnostic = EdronDiagnostic(
        "EDR-TOOL-0001", "error", "Problem", "Explain", context={"token": "private"}
    )
    assert diagnostic.to_mapping()["context"] == {"token": "<redacted>"}
    report = DiagnosticReport((diagnostic,))
    assert report.to_mapping()["ok"] is False
    assert report.to_sarif()["version"] == "2.1.0"


def test_static_check_does_not_import_source(tmp_path: Path) -> None:
    marker = tmp_path / "imported"
    source = tmp_path / "app.py"
    source.write_text(
        textwrap.dedent(
            f"""\n            from pathlib import Path
            Path({str(marker)!r}).write_text("bad")
            import edron as st
            """
        ),
        encoding="utf-8",
    )
    report = check_source(source)
    assert not marker.exists()
    assert report.diagnostics[0].code == "EDR-TOOL-0001"
    assert report.diagnostics[0].source == SourceLocation(str(source), 4, 1, 4, 19)


def test_explain_contains_source_mapped_registered_surfaces(tmp_path: Path) -> None:
    source = tmp_path / "app.py"
    source.write_text(
        textwrap.dedent(
            """\n            import edron as ed
            app = ed.App(title="Tooling", session_secret="test")
            @app.page("/", title="Home")
            class Home(ed.Page):
                @ed.fragment
                def status(self) -> None:
                    self.text("ready")
                def render(self) -> None:
                    self.status()
            """
        ),
        encoding="utf-8",
    )
    from edron.tooling import load_application

    app = load_application(source)
    payload = app.explain()
    assert payload["callbacks_executed"] is False
    assert payload["pages"][0]["surfaces"][0]["logical_id"] == "home-status"
    assert payload["pages"][0]["surfaces"][0]["source"]["start_line"] == 6


def test_function_page_is_explicit_and_request_compatible() -> None:
    app = ed.App(title="Function", session_secret="test")

    @app.function_page("/", title="Home")
    def home() -> str:
        return "value"

    response = TestClient(app.native).get("/")
    assert response.status_code == 200
    assert "value" in response.text
    assert app._function_pages[id(home)] in [record["type"] for record in app._pages.values()]


def test_descriptor_inheritance_is_explicit() -> None:
    app = ed.App(title="Inheritance", session_secret="test")

    class Shared(ed.Page):
        @ed.fragment
        def status(self) -> None:
            self.text("shared")

    @app.page("/", title="Home")
    class Home(Shared):
        status = ed.inherit(Shared.status)

        def render(self) -> None:
            self.status()

    assert app.native_surface(Home.status) is Home.status._native
    assert "shared" in TestClient(app.native).get("/").text


def test_scaffold_is_deterministic_and_refuses_overwrite(tmp_path: Path) -> None:
    paths = create_scaffold("My App", tmp_path / "app", template="form")
    assert {path.name for path in paths} == {"app.py", "README.md", "pyproject.toml"}
    assert "@ed.action" in (tmp_path / "app" / "app.py").read_text(encoding="utf-8")
    with pytest.raises(FileExistsError):
        create_scaffold("My App", tmp_path / "app", template="form")
