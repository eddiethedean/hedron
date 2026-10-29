"""Exercise the opt-in browser-test scaffold as a generated downstream project."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(
        os.environ.get("HEDRON_BROWSER") != "1",
        reason="Opt-in generated-project browser evidence: set HEDRON_BROWSER=1",
    ),
]


def test_opt_in_scaffold_generates_a_runnable_browser_test(tmp_path: Path) -> None:
    """Reuse the workspace environment because the candidate is not published yet."""
    project = tmp_path / "generated-app"
    creation = subprocess.run(
        [
            sys.executable,
            "-m",
            "hedron",
            "new",
            "generated-app",
            "--path",
            str(project),
            "--with-ui-tests",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert creation.returncode == 0, creation.stdout + creation.stderr

    engine = os.environ.get("HEDRON_BROWSER_ENGINE", "chromium")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--browser",
            engine,
            "-n",
            "0",
            "tests/test_ui.py",
        ],
        cwd=project,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "1 passed" in result.stdout
