#!/usr/bin/env python3
"""Fail if recipe docs Code tabs diverge from runnable examples (adoption guard)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _must_contain(path: Path, needles: list[str]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [n for n in needles if n not in text]


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
                '@app.command("/logout"',
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
                '@app.command("/save"',
                "refresh(notes)",
                "curl -fsSL https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/notes-sqlalchemy/app.py",
                "Real recipe",
            ],
        ),
        (
            ROOT / "docs/guides/authentication.md",
            [
                '@app.page("/login")',
                '@app.command("/logout"',
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
    if failed:
        return 1
    print("ok: recipe Code tabs match runnable markers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
