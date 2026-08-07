#!/usr/bin/env python3
"""Fail if adopter-facing docs claim a stale published train or banned maturity jargon.

The living line is 0.18.x. Historical whats-new / acceptance / RFC phase labels
are allowed. This check targets pages that assert "current" product maturity.

Also fails when adopter install snippets pin ``hedron>=0.18.0`` (or adapter
packages) without an upper bound ``,<0.19``.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Paths that must not assert 0.16.x or 0.17.x as the *current* line.
CHECKED = [
    ROOT / "docs" / "SECURITY.md",
    ROOT / "SECURITY.md",
    ROOT / "docs" / "getting-started" / "installation.md",
    ROOT / "docs" / "guides" / "troubleshooting.md",
    ROOT / "docs" / "guides" / "faq.md",
    ROOT / "docs" / "guides" / "evidence-pack.md",
    ROOT / "docs" / "examples" / "try-it.md",
    ROOT / "docs" / "guides" / "best-practices.md",
    ROOT / "docs" / "guides" / "whats-ready.md",
    ROOT / "docs" / "guides" / "evaluate.md",
    ROOT / "docs" / "guides" / "upgrade.md",
    ROOT / "docs" / "getting-started" / "how-to-read.md",
    ROOT / "README.md",
]

# Patterns that indicate stale "current train" claims (not historical mentions).
STALE = [
    re.compile(r"current published train[^\n]*0\.16", re.I),
    re.compile(r"current published train[^\n]*0\.17", re.I),
    re.compile(r"train is \*\*0\.16\.x\*\*", re.I),
    re.compile(r"latest published train is \*\*0\.16", re.I),
    re.compile(r"Expect \*\*`0\.17\.0`\*\*", re.I),
    re.compile(r"matching `0\.16\.x` pin", re.I),
    re.compile(r"hedron==0\.17\.0", re.I),
    re.compile(r"verify_pkg_15\.py", re.I),
    re.compile(r"hedron>=0\.17\.0", re.I),
    re.compile(r"capture UI remains Deferred", re.I),
    re.compile(r"Supported lines: \*\*`0\.16\.x`", re.I),
]

# Adopter-facing jargon / maturity collisions banned on checked entry pages.
# Historical whats-new / RFCs are not in CHECKED.
BANNED = [
    re.compile(r"Supported beta", re.I),
    re.compile(r"Maturity SSOT"),
    re.compile(r"beachhead Supported", re.I),
    re.compile(r"as Supported beachhead", re.I),
    re.compile(r"Still Deferred \(after"),
]

# Install pins that omit the 0.19 upper bound (allows a future breaking train).
# Matches: "hedron>=0.18.0", hedron>=0.18.0, hedron[data]>=0.18.0, hedron-flask>=0.18.0
# Does not match when immediately followed by ,<0.19 (quoted or unquoted).
UNBOUNDED_PIN = re.compile(
    r"(?:hedron(?:\[[^\]]+\])?|hedron-(?:flask|django|core|data|explorer|jinja|"
    r"conformance|extras))"
    r">=0\.18\.0"
    r"(?!,?\s*<0\.19)"
)

# Bare extras with no version at all: "hedron[data]", 'hedron[jinja]', hedron[charts]
# (Alpha charts/notebook/mcp/gradio/native should use >=0.1.0,<0.2).
BARE_EXTRA = re.compile(r"""["']hedron\[[^\]]+\]["'](?!\s*>=)""")

# Alpha extras pinned without an upper bound: >=0.1.0 not followed by ,<0.2
UNBOUNDED_ALPHA = re.compile(
    r"hedron\[(?:charts|notebook|mcp|gradio|native)\]>=0\.1\.0(?!,?\s*<0\.2)"
)

# Paths scanned for unbounded pins (adopter-facing; exclude historical archives).
PIN_SCAN_ROOTS = [
    ROOT / "docs" / "getting-started",
    ROOT / "docs" / "guides",
    ROOT / "docs" / "examples",
    ROOT / "docs" / "api",
    ROOT / "docs" / "components",
    ROOT / "docs" / "index.md",
    ROOT / "README.md",
    ROOT / "packages" / "hedron" / "README.md",
]

# Basename prefixes that may discuss historical trains without current install advice.
PIN_SKIP_NAME_PREFIXES = (
    "whats-new-0.",
    "RELEASE_0_",
)

# Lines that *warn about* the unbounded form (not install advice).
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
                    f"{path.relative_to(ROOT)}:{lineno}: unbounded 0.18 pin "
                    f"(use >=0.18.0,<0.19): {line.strip()[:120]}"
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
        "ok: adopter docs assert 0.18, upper-bound pins, and avoid "
        "Supported beta / SSOT / beachhead jargon"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
