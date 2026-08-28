from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE = tomllib.loads((ROOT / "docs" / "release.toml").read_text(encoding="utf-8"))["release"]
PIN = f">={RELEASE['pin_floor']},<{RELEASE['pin_ceiling']}"
FIRST_RUN_PIN = (
    f">={RELEASE['pypi_pin_floor']},<{RELEASE['pypi_pin_ceiling']}"
    if RELEASE.get("registry_status") == "deferred"
    else PIN
)

VSCODE_PATH = ROOT / "docs" / "getting-started" / "first-app-vscode.md"
POSIT_PATH = ROOT / "docs" / "getting-started" / "first-app-posit-workbench.md"


def test_beginner_guides_are_in_navigation_and_start_page() -> None:
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    start = (ROOT / "docs" / "getting-started" / "index.md").read_text(encoding="utf-8")

    for filename in (VSCODE_PATH.name, POSIT_PATH.name):
        assert f"getting-started/{filename}" in nav
        assert f"({filename})" in start


def test_task_finding_pages_are_in_navigation() -> None:
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    for path in (
        "getting-started/core-concepts.md",
        "getting-started/interaction-apis.md",
        "guides/cookbook.md",
        "guides/troubleshooting.md",
        "guides/error-codes.md",
    ):
        assert path in nav


def test_vscode_guide_uses_the_current_flagship_train_without_posit() -> None:
    guide = VSCODE_PATH.read_text(encoding="utf-8")

    assert f'uvx --from "hedron{FIRST_RUN_PIN}" hedron new my-hedron-app' in guide
    assert "uv run uvicorn app:app --reload" in guide
    assert "uv run pytest" in guide
    assert "hedron-posit>=" not in guide


def test_workbench_guide_uses_the_preferred_hedron_posit_surface() -> None:
    guide = POSIT_PATH.read_text(encoding="utf-8")

    assert "python3.11 -m venv .venv" in guide
    assert (
        'python3.11 -m pip install "hedron>=0.67.0,<0.68" "hedron-posit>=0.67.0"'
        in guide
    )
    assert "hedron new my-workbench-app --path . --force" in guide
    assert 'python3.11 -m pip install "hedron>=0.66.2,<0.67"' not in guide
    assert 'python3.11 -m pip install -e . "hedron-posit>=0.67.0"' not in guide
    assert "pyenv install" in guide
    assert "pyenv local" in guide
    assert "from hedron_posit import HedronPosit" in guide
    assert "app = HedronPosit(" in guide
    assert "hedron-posit check" in guide
    assert "hedron-posit run app:app --port 8000 --reload" in guide
    assert "uv add" not in guide
    assert "uv run" not in guide
    assert "\ndeactivate\n" not in guide
    assert "from hedron_workbench import HedronWorkbench" not in guide
