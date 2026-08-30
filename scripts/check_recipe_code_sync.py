#!/usr/bin/env python3
"""Fail if recipe docs Code tabs diverge from runnable examples (adoption guard)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _must_contain(path: Path, needles: list[str]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [n for n in needles if n not in text]


def _titled_code_blocks(path: Path) -> dict[str, str]:
    """Return titled source-code blocks keyed by their title."""
    lines = path.read_text(encoding="utf-8").splitlines()
    blocks: dict[str, str] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        match = re.fullmatch(r'\s*```(?:python|css|toml) title="([^"]+)"\s*', line)
        if match is None:
            index += 1
            continue
        title = match.group(1)
        indent = line[: len(line) - len(line.lstrip())]
        body: list[str] = []
        index += 1
        while index < len(lines) and lines[index].strip() != "```":
            body_line = lines[index]
            body.append(body_line[len(indent) :] if body_line.startswith(indent) else body_line)
            index += 1
        blocks[title] = "\n".join(body).rstrip() + "\n"
        index += 1
    return blocks


def _source_tab_errors(doc: Path, sources: list[str]) -> list[str]:
    if not doc.is_file():
        return [f"missing: {doc.relative_to(ROOT)}"]
    blocks = _titled_code_blocks(doc)
    errors: list[str] = []
    for source in sources:
        source_path = ROOT / "examples/composable-app" / source
        if not source_path.is_file():
            errors.append(f"missing: {source_path.relative_to(ROOT)}")
            continue
        documented = blocks.get(source)
        if documented is None:
            errors.append(f"{doc.relative_to(ROOT)}: missing source tab {source!r}")
            continue
        actual = source_path.read_text(encoding="utf-8").rstrip() + "\n"
        if documented != actual:
            errors.append(
                f"{doc.relative_to(ROOT)}: tab {source!r} differs from "
                f"{source_path.relative_to(ROOT)}"
            )
    return errors


def main() -> int:
    checks: list[tuple[Path, list[str]]] = [
        (
            ROOT / "docs/examples/jobs-poll.md",
            [
                "enqueue_durable",
                "job_status_response",
                "Poll(",
                "curl -fsSL https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/jobs-poll/app.py",
                "Demo tab is a simplified",
            ],
        ),
        (
            ROOT / "docs/examples/session-auth.md",
            [
                '@app.page("/login")',
                '@app.action("/logout"',
                'RedirectResponse("/login"',
                "curl -fsSL https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/session-auth/app.py",
                "Real recipe",
            ],
        ),
        (
            ROOT / "docs/examples/file-upload.md",
            [
                "curl -fsSL https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/file-upload/app.py",
            ],
        ),
        (
            ROOT / "docs/examples/notes-sqlalchemy.md",
            [
                "create_engine",
                "sqlalchemy",
                '@app.action("/save"',
                "refresh(notes)",
                "curl -fsSL https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/notes-sqlalchemy/app.py",
                "Real recipe",
            ],
        ),
        (
            ROOT / "docs/guides/authentication.md",
            [
                '@app.page("/login")',
                '@app.action("/logout"',
                "examples/session-auth",
            ],
        ),
    ]
    failed = False
    for path, needles in checks:
        if not path.is_file():
            print(f"missing: {path.relative_to(ROOT)}", file=sys.stderr)
            failed = True
            continue
        missing = _must_contain(path, needles)
        if missing:
            failed = True
            rel = path.relative_to(ROOT)
            print(f"{rel}: missing required markers:", file=sys.stderr)
            for m in missing:
                print(f"  - {m!r}", file=sys.stderr)
    source_errors = _source_tab_errors(
        ROOT / "docs/examples/composable-app.md",
        [
            "app.py",
            "components/__init__.py",
            "components/metrics.py",
            "components/activity.py",
            "components/deployments.py",
            "components/status.py",
            "custom_css.py",
            "styles.css",
            "pyproject.toml",
        ],
    )
    if source_errors:
        failed = True
        for error in source_errors:
            print(error, file=sys.stderr)
    if failed:
        return 1
    print("ok: recipe Code tabs match runnable markers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
