from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import check_docs_train_ssot as ssot  # noqa: E402

FIRST_RUN_PIN = (
    ssot.FACTS.pypi_pin if ssot.FACTS.registry_deferred else ssot.MINIMUM_COMPATIBILITY_PIN
)
# 1.0.0/1.0.1 resolved an incomplete fastapi-workbench artifact. Keep the
# Workbench walkthrough on the first corrected immutable package pair.
POSIT_FIRST_RUN_PIN = ">=1.0.2"

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
    install = (
        f'python3.11 -m pip install "hedron{FIRST_RUN_PIN}" "hedron-posit{POSIT_FIRST_RUN_PIN}"'
    )
    assert install in guide
    assert "hedron new my-workbench-app --path . --force" in guide
    assert 'python3.11 -m pip install "hedron>=0.66.2,<0.67"' not in guide
    assert 'python3.11 -m pip install -e . "hedron-posit' not in guide
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
