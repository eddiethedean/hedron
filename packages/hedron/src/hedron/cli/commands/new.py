"""CLI command: scaffold a Hedron application or element."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from hedron.cli.scaffold.django import _scaffold_django
from hedron.cli.scaffold.element import _scaffold_element
from hedron.cli.scaffold.fastapi import _scaffold_fastapi
from hedron.cli.scaffold.flask import _scaffold_flask


def _contains_only_project_venv(dest: Path) -> bool:
    """Allow the beginner-friendly project-first flow without weakening overwrite safety."""
    return dest.is_dir() and (dest / ".venv").is_dir() and all(
        entry.name == ".venv" for entry in dest.iterdir()
    )


def _cmd_new(args: argparse.Namespace) -> int:
    if args.name == "element":
        if not args.element_name:
            print("hedron new element requires an element name", file=sys.stderr)
            return 2
        return _cmd_new_element(args)
    if args.element_name is not None:
        print("Unexpected second name; use 'hedron new element <name>'", file=sys.stderr)
        return 2
    dest = Path(args.path or args.name).resolve()
    if (
        dest.exists()
        and any(dest.iterdir())
        and not args.force
        and not _contains_only_project_venv(dest)
    ):
        print(f"Refusing to overwrite non-empty {dest} (use --force)", file=sys.stderr)
        return 1
    framework = "fastapi"
    if getattr(args, "flask", False):
        framework = "flask"
    if getattr(args, "django", False):
        framework = "django"
    if getattr(args, "flask", False) and getattr(args, "django", False):
        print("Choose at most one of --flask / --django", file=sys.stderr)
        return 1
    template = str(getattr(args, "template", None) or "minimal")
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
    if any(path.exists() for path in guarded) and not args.force:
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
    name = str(args.element_name)
    dest = Path(args.path or name).resolve()
    if dest.exists() and any(dest.iterdir()) and not args.force:
        print(f"Refusing to overwrite non-empty {dest} (use --force)", file=sys.stderr)
        return 1
    guarded = [dest / "pyproject.toml", dest / "src", dest / "tests", dest / "examples"]
    if any(path.exists() for path in guarded) and not args.force:
        existing = ", ".join(str(path) for path in guarded if path.exists())
        print(f"Refusing to overwrite existing {existing} (use --force)", file=sys.stderr)
        return 1
    dest.mkdir(parents=True, exist_ok=True)
    return _scaffold_element(name, dest)
