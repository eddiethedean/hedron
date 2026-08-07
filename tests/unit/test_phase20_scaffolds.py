"""Phase 0.20 SCAFFOLD-020: hedron new --flask / --django."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run_new(*extra: str, dest: Path) -> dict[str, object]:
    proc = subprocess.run(
        [sys.executable, "-m", "hedron", "new", "demo", "--path", str(dest), "--force", *extra],
        check=True,
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parents[1],
    )
    return json.loads(proc.stdout)


def test_scaffold_flask(tmp_path: Path) -> None:
    dest = tmp_path / "flask-app"
    payload = _run_new("--flask", dest=dest)
    assert payload["framework"] == "flask"
    text = (dest / "pyproject.toml").read_text(encoding="utf-8")
    assert "hedron-flask" in text
    assert "fastapi" not in text.lower()
    assert "uvicorn" not in text.lower()
    app = (dest / "app.py").read_text(encoding="utf-8")
    assert "fragment_regions" in app
    assert "replace-in-production" in app
    assert "HedronFlask" in app


def test_scaffold_django(tmp_path: Path) -> None:
    dest = tmp_path / "django-app"
    payload = _run_new("--django", dest=dest)
    assert payload["framework"] == "django"
    text = (dest / "pyproject.toml").read_text(encoding="utf-8")
    assert "hedron-django" in text
    assert "fastapi" not in text.lower()
    assert (dest / "project" / "settings.py").is_file()
    urls = (dest / "project" / "urls.py").read_text(encoding="utf-8")
    assert "fragment_regions" in urls
    assert "HedronSecurityHeadersMiddleware" in (dest / "project" / "settings.py").read_text(
        encoding="utf-8"
    )


def test_scaffold_fastapi_default(tmp_path: Path) -> None:
    dest = tmp_path / "fastapi-app"
    payload = _run_new(dest=dest)
    assert payload.get("framework", "fastapi") == "fastapi"
    assert "hedron>=" in (dest / "pyproject.toml").read_text(encoding="utf-8")
