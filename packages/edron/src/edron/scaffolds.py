"""Small, reviewable Edron teaching scaffolds."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Final

TEMPLATES: Final[tuple[str, ...]] = ("minimal", "dashboard", "form")


def _project_name(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower()
    if not normalized:
        raise ValueError("project name must contain a letter or number")
    return normalized


def _app(template: str, name: str) -> str:
    if template == "dashboard":
        body = (
            '        self.metric("Orders", 128, delta="+12")\n'
            '        self.text("Start with a fragment when a panel needs independent refresh.")\n'
        )
    elif template == "form":
        body = (
            '        self.text("Add an action with a typed Pydantic model when this form '
            'becomes real.")\n'
            '        self.button("Save", action=self.save)\n\n'
            "    @ed.action\n"
            "    def save(self) -> ed.Outcome:\n"
            '        return ed.success("Saved in the teaching scaffold")\n'
        )
    else:
        body = '        self.text("A request-local Page instance owns this render only.")\n'
    return f'''"""Edron {template} teaching scaffold.

Replace the example values and keep application state in explicit dependencies.
"""

import edron as ed

app = ed.App(title={name!r}, security="standard", session_secret="replace-in-production")


@app.page("/", title={name!r})
class Home(ed.Page):
    def render(self) -> None:
{body}'''


def create_scaffold(
    name: str,
    destination: str | Path,
    *,
    template: str = "minimal",
    overwrite: bool = False,
) -> tuple[Path, ...]:
    """Create a deterministic Edron project without importing the generated app."""
    if template not in TEMPLATES:
        raise ValueError(f"unknown Edron template {template!r}; choose from {', '.join(TEMPLATES)}")
    root = Path(destination)
    if root.exists() and any(root.iterdir()) and not overwrite:
        raise FileExistsError(f"destination is not empty: {root}")
    root.mkdir(parents=True, exist_ok=True)
    project = _project_name(name)
    pyproject = f'''[project]
name = "{project}"
version = "0.1.0"
requires-python = ">=3.10,<3.15"
dependencies = [
    "edron>=1.0.0,<2.0",
    "hedron>=1.0.0,<2.0",
    "hedron-data>=1.0.0,<2.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
'''
    readme = f"# {name}\n\nGenerated with `edron new --template {template}`.\n"
    files = {
        root / "pyproject.toml": pyproject,
        root / "app.py": _app(template, name),
        root / "README.md": readme,
    }
    if not overwrite:
        existing = [path for path in files if path.exists()]
        if existing:
            raise FileExistsError(f"refusing to overwrite {existing[0]}")
    for path, content in files.items():
        path.write_text(content, encoding="utf-8")
    return tuple(files)


__all__ = ["TEMPLATES", "create_scaffold"]
