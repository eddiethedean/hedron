"""CLI command: scaffold a Hedron application or element."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Protocol, cast

from hedron.cli.scaffold.django import scaffold_django as _scaffold_django
from hedron.cli.scaffold.element import scaffold_element as _scaffold_element
from hedron.cli.scaffold.fastapi import scaffold_fastapi as _scaffold_fastapi
from hedron.cli.scaffold.flask import scaffold_flask as _scaffold_flask


class _NewArgs(Protocol):
    name: str
    element_name: str | None
    path: str | None
    force: bool
    flask: bool
    django: bool
    template: str | None


def _contains_only_project_venv(dest: Path) -> bool:
    """Allow the beginner-friendly project-first flow without weakening overwrite safety."""
    return (
        dest.is_dir()
        and (dest / ".venv").is_dir()
        and all(entry.name == ".venv" for entry in dest.iterdir())
    )


def _cmd_new(args: argparse.Namespace) -> int:
    typed_args = cast(_NewArgs, cast(object, args))
    if typed_args.name == "element":
        if not typed_args.element_name:
            print("hedron new element requires an element name", file=sys.stderr)
            return 2
        return _cmd_new_element(args)
    if typed_args.element_name is not None:
        print("Unexpected second name; use 'hedron new element <name>'", file=sys.stderr)
        return 2
    dest = Path(typed_args.path or typed_args.name).resolve()
    if (
        dest.exists()
        and any(dest.iterdir())
        and not typed_args.force
        and not _contains_only_project_venv(dest)
    ):
        print(f"Refusing to overwrite non-empty {dest} (use --force)", file=sys.stderr)
        return 1
    framework = "fastapi"
    if typed_args.flask:
        framework = "flask"
    if typed_args.django:
        framework = "django"
    if typed_args.flask and typed_args.django:
        print("Choose at most one of --flask / --django", file=sys.stderr)
        return 1
    template = typed_args.template or "minimal"
    if framework != "fastapi" and template != "minimal":
        print(
            f"--template {template!r} is only supported for the FastAPI scaffold",
            file=sys.stderr,
        )
        return 2

    if framework == "fastapi" or framework == "flask":
        guarded = [dest / "app.py", dest / "pyproject.toml"]
    else:
        guarded = [dest / "manage.py", dest / "pyproject.toml", dest / "project"]
    if any(path.exists() for path in guarded) and not typed_args.force:
        existing = ", ".join(str(p) for p in guarded if p.exists())
        print(f"Refusing to overwrite existing {existing} (use --force)", file=sys.stderr)
        return 1
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "components").mkdir(exist_ok=True)

    if framework == "fastapi":
        return _scaffold_fastapi(args, dest)
    if framework == "flask":
        return _scaffold_flask(args, dest)
    return _scaffold_django(args, dest)


def _cmd_new_element(args: argparse.Namespace) -> int:
    typed_args = cast(_NewArgs, cast(object, args))
    name = str(typed_args.element_name)
    dest = Path(typed_args.path or name).resolve()
    if dest.exists() and any(dest.iterdir()) and not typed_args.force:
        print(f"Refusing to overwrite non-empty {dest} (use --force)", file=sys.stderr)
        return 1
    guarded = [dest / "pyproject.toml", dest / "src", dest / "tests", dest / "examples"]
    if any(path.exists() for path in guarded) and not typed_args.force:
        existing = ", ".join(str(path) for path in guarded if path.exists())
        print(f"Refusing to overwrite existing {existing} (use --force)", file=sys.stderr)
        return 1
    dest.mkdir(parents=True, exist_ok=True)
    return _scaffold_element(name, dest)


cmd_new = _cmd_new
