from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE = tomllib.loads((ROOT / "docs" / "release.toml").read_text(encoding="utf-8"))["release"]
PIN = f">={RELEASE['pin_floor']},<{RELEASE['pin_ceiling']}"

VSCODE_PATH = ROOT / "docs" / "getting-started" / "first-app-vscode.md"
POSIT_PATH = ROOT / "docs" / "getting-started" / "first-app-posit-workbench.md"


def test_beginner_guides_are_in_navigation_and_start_page() -> None:
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    start = (ROOT / "docs" / "getting-started" / "index.md").read_text(encoding="utf-8")

    for filename in (VSCODE_PATH.name, POSIT_PATH.name):
        assert f"getting-started/{filename}" in nav
        assert f"({filename})" in start


def test_vscode_guide_uses_the_current_flagship_train_without_posit() -> None:
    guide = VSCODE_PATH.read_text(encoding="utf-8")

    assert f'uvx --from "hedron{PIN}" hedron new my-hedron-app' in guide
    assert "uv run uvicorn app:app --reload" in guide
    assert "uv run pytest" in guide
    assert "hedron-posit>=" not in guide


def test_workbench_guide_uses_the_preferred_hedron_posit_surface() -> None:
    guide = POSIT_PATH.read_text(encoding="utf-8")

    assert f'uv add "hedron-posit{PIN}"' in guide
    assert "from hedron_posit import HedronPosit" in guide
    assert "app = HedronPosit(" in guide
    assert "uv run hedron-posit check" in guide
    assert "uv run hedron-posit run app:app --reload" in guide
    assert "from hedron_workbench import HedronWorkbench" not in guide
