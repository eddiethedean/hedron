#!/usr/bin/env python3
"""Fail if adopter-facing docs claim a stale published train or banned maturity jargon.

The living line is 0.19.x on ``main`` (ready to cut). Last published PyPI/git is
``v0.18.0`` until ``v0.19.0`` is tagged. Historical whats-new / acceptance /
RFC phase labels are allowed. This check targets pages that assert "current"
product maturity.

Also fails when adopter install snippets pin ``hedron>=0.19.0`` (or adapter
packages) without an upper bound ``,<0.20``.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Paths that must not assert a stale *current* line or premature Published 0.19.
CHECKED = [
    ROOT / "docs" / "SECURITY.md",
    ROOT / "SECURITY.md",
    ROOT / "docs" / "STATUS.md",
    ROOT / "docs" / "RELEASE.md",
    ROOT / "docs" / "index.md",
    ROOT / "docs" / "COMPATIBILITY.md",
    ROOT / "docs" / "getting-started" / "installation.md",
    ROOT / "docs" / "guides" / "troubleshooting.md",
    ROOT / "docs" / "guides" / "faq.md",
    ROOT / "docs" / "guides" / "evidence-pack.md",
    ROOT / "docs" / "examples" / "try-it.md",
    ROOT / "docs" / "guides" / "best-practices.md",
    ROOT / "docs" / "guides" / "whats-ready.md",
    ROOT / "docs" / "guides" / "evaluate.md",
    ROOT / "docs" / "guides" / "upgrade.md",
    ROOT / "docs" / "guides" / "release-notes.md",
    ROOT / "docs" / "guides" / "whats-new-0.19.md",
    ROOT / "docs" / "getting-started" / "how-to-read.md",
    ROOT / "README.md",
    ROOT / "packages" / "hedron" / "README.md",
    ROOT / "packages" / "hedron-core" / "README.md",
    ROOT / "packages" / "hedron-data" / "README.md",
    ROOT / "packages" / "hedron-flask" / "README.md",
    ROOT / "packages" / "hedron-django" / "README.md",
    ROOT / "packages" / "hedron-explorer" / "README.md",
    ROOT / "scripts" / "README.md",
]

# Patterns that indicate stale "current train" claims (not historical mentions).
STALE = [
    re.compile(r"current published train[^\n]*0\.16", re.I),
    re.compile(r"current published train[^\n]*0\.17", re.I),
    re.compile(r"train is \*\*0\.16\.x\*\*", re.I),
    re.compile(r"latest published train is \*\*0\.16", re.I),
    re.compile(r"Expect \*\*`0\.17\.0`\*\*", re.I),
    re.compile(r"Expect \*\*`0\.18\.0`\*\*", re.I),
    re.compile(r"matching `0\.16\.x` pin", re.I),
    re.compile(r"matching `0\.18\.x` pin", re.I),
    re.compile(r"hedron==0\.17\.0", re.I),
    re.compile(r"verify_pkg_15\.py", re.I),
    re.compile(r"hedron>=0\.17\.0", re.I),
    re.compile(r"capture UI remains Deferred", re.I),
    re.compile(r"Supported lines: \*\*`0\.16\.x`", re.I),
    re.compile(r"Current train — 0\.18", re.I),
    re.compile(r"Current train: \*\*0\.18", re.I),
    re.compile(r"Coordinated train: \*\*`0\.18", re.I),
    re.compile(r"Python-first UI framework · v0\.18", re.I),
    re.compile(r"Pin the \*\*0\.18 train\*\*", re.I),
    re.compile(r"expects \*\*0\.18\*\*", re.I),
    # Premature Published claims before the v0.19.0 tag exists.
    re.compile(r"Published\*\* as `v0\.19\.0`", re.I),
    re.compile(r"\*\*Published:\*\* `v0\.19\.0`", re.I),
    re.compile(r"Last published train:\*\* `v0\.19\.0`", re.I),
    re.compile(r"phase 0\.19 \*\*Published\*\*", re.I),
]

# Adopter-facing jargon / maturity collisions banned on checked entry pages.
BANNED = [
    re.compile(r"Supported beta", re.I),
    re.compile(r"Maturity SSOT"),
    re.compile(r"beachhead Supported", re.I),
    re.compile(r"as Supported beachhead", re.I),
    re.compile(r"Still Deferred \(after"),
]

UNBOUNDED_PIN = re.compile(
    r"(?:hedron(?:\[[^\]]+\])?|hedron-(?:flask|django|core|data|explorer|jinja|"
    r"conformance|extras))"
    r">=0\.19\.0"
    r"(?!,?\s*<0\.20)"
)

BARE_EXTRA = re.compile(r"""["']hedron\[[^\]]+\]["'](?!\s*>=)""")

UNBOUNDED_ALPHA = re.compile(
    r"hedron\[(?:charts|notebook|mcp|gradio|native)\]>=0\.1\.0(?!,?\s*<0\.2)"
)

PIN_SCAN_ROOTS = [
    ROOT / "docs" / "getting-started",
    ROOT / "docs" / "guides",
    ROOT / "docs" / "examples",
    ROOT / "docs" / "api",
    ROOT / "docs" / "components",
    ROOT / "docs" / "index.md",
    ROOT / "README.md",
    ROOT / "packages" / "hedron" / "README.md",
    ROOT / "packages" / "hedron-conformance" / "README.md",
    ROOT / "examples" / "hdj-progressive" / "README.md",
]

PIN_SKIP_NAME_PREFIXES = (
    "whats-new-0.",
    "RELEASE_0_",
)

PIN_ALLOW_SUBSTRINGS = (
    "alone allows a future",
    "without an upper bound",
)


def _pin_scan_files() -> list[Path]:
    files: list[Path] = []
    for root in PIN_SCAN_ROOTS:
        if root.is_file():
            files.append(root)
            continue
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.md")):
            name = path.name
            if any(name.startswith(prefix) for prefix in PIN_SKIP_NAME_PREFIXES):
                continue
            files.append(path)
    return files


def _check_unbounded_pins() -> list[str]:
    failures: list[str] = []
    for path in _pin_scan_files():
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if any(allow in line for allow in PIN_ALLOW_SUBSTRINGS):
                continue
            if UNBOUNDED_PIN.search(line):
                failures.append(
                    f"{path.relative_to(ROOT)}:{lineno}: unbounded 0.19 pin "
                    f"(use >=0.19.0,<0.20): {line.strip()[:120]}"
                )
            if BARE_EXTRA.search(line):
                failures.append(
                    f"{path.relative_to(ROOT)}:{lineno}: bare hedron[extra] "
                    f"(add >=…,<… pin): {line.strip()[:120]}"
                )
            if UNBOUNDED_ALPHA.search(line):
                failures.append(
                    f"{path.relative_to(ROOT)}:{lineno}: unbounded Alpha pin "
                    f"(use >=0.1.0,<0.2): {line.strip()[:120]}"
                )
    return failures


def main() -> int:
    failures: list[str] = []
    for path in CHECKED:
        if not path.is_file():
            failures.append(f"missing file: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in STALE:
            if pattern.search(text):
                failures.append(f"{path.relative_to(ROOT)}: matches {pattern.pattern}")
        for pattern in BANNED:
            if pattern.search(text):
                failures.append(f"{path.relative_to(ROOT)}: banned {pattern.pattern}")
    failures.extend(_check_unbounded_pins())
    if failures:
        print("stale, banned, or unbounded adopter-doc claims:", file=sys.stderr)
        for item in failures:
            print(f"  {item}", file=sys.stderr)
        return 1
    print(
        "ok: adopter docs assert 0.19 (ready-to-cut), upper-bound pins, and avoid "
        "Supported beta / SSOT / beachhead jargon"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
