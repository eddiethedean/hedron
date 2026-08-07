"""Phase 0.19 ATAG-019."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hedron_core import reset_registry_for_tests
from hedron_core.a11y import default_contract


@pytest.fixture(autouse=True)
def _fresh_registry() -> None:
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    yield


def _write_project(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname='demo'\nversion='0.0.0'\n[tool.hedron]\n",
        encoding="utf-8",
    )


def test_inspect_includes_accessibility_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _write_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    from hedron.cli import main

    with pytest.raises(SystemExit) as exc:
        main(["inspect", "Button"])
    assert exc.value.code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["accessibility_contract"]["component"] == "Button"
    assert data["accessibility_contract"]["reviewed"] is True
    assert data["accessibility_props_alongside_ordinary"] is True
    assert data["repair_guidance"]["reversible"] is True


def test_eject_preserves_accessibility_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    from hedron.cli import main

    out = tmp_path / "ejected"
    with pytest.raises(SystemExit) as exc:
        main(["eject", "Button", "--out", str(out), "--force"])
    assert exc.value.code == 0
    contract_file = out / "accessibility_contract.json"
    assert contract_file.is_file()
    data = json.loads(contract_file.read_text(encoding="utf-8"))
    assert data["component"] == "Button"
    assert data["reviewed"] is True
    assert data["implies_application_conformance"] is False
    again = default_contract(data["component"], notes=data.get("notes") or "")
    assert again.component == "Button"
