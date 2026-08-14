#!/usr/bin/env python3
"""Reject missing links and links to files excluded from the published docs site."""

from __future__ import annotations

import fnmatch
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MKDOCS = ROOT / "mkdocs.yml"
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")


def exclusion_patterns(config: str) -> tuple[str, ...]:
    lines = config.splitlines()
    try:
        start = lines.index("exclude_docs: |") + 1
    except ValueError as exc:
        raise ValueError("mkdocs.yml has no literal exclude_docs block") from exc
    patterns: list[str] = []
    for line in lines[start:]:
        if line and not line.startswith("  "):
            break
        value = line.strip()
        if value and not value.startswith("#"):
            patterns.append(value.removeprefix("/"))
    return tuple(patterns)


def is_excluded(relative: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatchcase(relative, pattern) for pattern in patterns)


def published_markdown(patterns: tuple[str, ...]) -> list[Path]:
    return [
        path
        for path in sorted(DOCS.rglob("*.md"))
        if not path.is_symlink() and not is_excluded(path.relative_to(DOCS).as_posix(), patterns)
    ]


def check_links(path: Path, patterns: tuple[str, ...]) -> list[str]:
    text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.DOTALL)
    failures: list[str] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for raw_target in LINK_PATTERN.findall(line):
            target = raw_target.strip("<>")
            parsed = urllib.parse.urlsplit(target)
            if parsed.scheme or parsed.netloc or target.startswith(("#", "mailto:")):
                continue
            local = urllib.parse.unquote(parsed.path)
            if not local:
                continue
            resolved = (path.parent / local).resolve()
            display = path.relative_to(ROOT)
            if not resolved.exists():
                failures.append(f"{display}:{line_number}: missing link target {target!r}")
                continue
            try:
                relative_doc = resolved.relative_to(DOCS).as_posix()
            except ValueError:
                continue
            if is_excluded(relative_doc, patterns):
                failures.append(
                    f"{display}:{line_number}: {target!r} is excluded from MkDocs; "
                    "use a public page or an absolute GitHub link"
                )
    return failures


def main() -> int:
    patterns = exclusion_patterns(MKDOCS.read_text(encoding="utf-8"))
    paths = published_markdown(patterns)
    failures = [failure for path in paths for failure in check_links(path, patterns)]
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"ok: links in {len(paths)} published Markdown pages resolve to published targets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
