#!/usr/bin/env python3
"""Fail if adopter-facing docs claim a stale published train or banned maturity jargon.

The living published line is 0.22.x (``v0.22.0``). Historical whats-new / acceptance /
RFC phase labels are allowed. This check targets pages that assert "current"
product maturity.

Also fails when adopter install snippets pin ``hedron>=0.22.0`` (or adapter
packages) without an upper bound ``,<0.23``.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Paths that must not assert a stale *current* line or leftover Ready-to-cut 0.21.
CHECKED = [
    ROOT / "docs" / "SECURITY.md",
    ROOT / "SECURITY.md",
    ROOT / "docs" / "STATUS.md",
    ROOT / "docs" / "RELEASE.md",
    ROOT / "docs" / "index.md",
    ROOT / "docs" / "COMPATIBILITY.md",
    ROOT / "docs" / "PERFORMANCE_BUDGETS.md",
    ROOT / "docs" / "PROJECT_LAYOUT.md",
    ROOT / "docs" / "overrides" / "main.html",
    ROOT / "docs" / "getting-started" / "installation.md",
    ROOT / "docs" / "getting-started" / "quickstart.md",
    ROOT / "docs" / "getting-started" / "how-to-read.md",
    ROOT / "docs" / "getting-started" / "index.md",
    ROOT / "docs" / "guides" / "troubleshooting.md",
    ROOT / "docs" / "guides" / "faq.md",
    ROOT / "docs" / "guides" / "evidence-pack.md",
    ROOT / "docs" / "guides" / "enterprise-diligence.md",
    ROOT / "docs" / "guides" / "threat-model.md",
    ROOT / "docs" / "guides" / "changelog.md",
    ROOT / "docs" / "guides" / "index.md",
    ROOT / "docs" / "guides" / "production-readiness.md",
    ROOT / "docs" / "guides" / "production-quality.md",
    ROOT / "docs" / "guides" / "dashboards.md",
    ROOT / "docs" / "guides" / "performance.md",
    ROOT / "docs" / "guides" / "whats-new-0.15.md",
    ROOT / "docs" / "examples" / "try-it.md",
    ROOT / "docs" / "guides" / "best-practices.md",
    ROOT / "docs" / "guides" / "whats-ready.md",
    ROOT / "docs" / "guides" / "evaluate.md",
    ROOT / "docs" / "guides" / "upgrade.md",
    ROOT / "docs" / "guides" / "release-notes.md",
    ROOT / "docs" / "guides" / "whats-new-0.21.md",
    ROOT / "docs" / "guides" / "whats-new-0.22.md",
    ROOT / "docs" / "guides" / "roadmap.md",
    ROOT / "docs" / "api" / "ADAPTERS.md",
    ROOT / "docs" / "api" / "INTERACTION.md",
    ROOT / "docs" / "api" / "STABILITY.md",
    ROOT / "docs" / "api" / "README.md",
    ROOT / "docs" / "api" / "HEDRON.md",
    ROOT / "docs" / "packages" / "index.md",
    ROOT / "README.md",
    ROOT / "packages" / "hedron" / "README.md",
    ROOT / "packages" / "hedron-core" / "README.md",
    ROOT / "packages" / "hedron-data" / "README.md",
    ROOT / "packages" / "hedron-flask" / "README.md",
    ROOT / "packages" / "hedron-django" / "README.md",
    ROOT / "packages" / "hedron-explorer" / "README.md",
    ROOT / "packages" / "hedron-extras" / "README.md",
    ROOT / "packages" / "hedron-charts" / "README.md",
    ROOT / "docs" / "packages" / "hedron-jinja.md",
    ROOT / "docs" / "packages" / "hedron-data.md",
    ROOT / "docs" / "packages" / "hedron-explorer.md",
    ROOT / "docs" / "packages" / "hedron-conformance.md",
    ROOT / "docs" / "api" / "CSRF_COMPOSITION.md",
    ROOT / "mkdocs.yml",
    ROOT / "packages" / "hedron-jinja" / "README.md",
    ROOT / "packages" / "hedron-conformance" / "README.md",
    ROOT / "docs" / "packages" / "hedron-extras.md",
    ROOT / "scripts" / "README.md",
    ROOT / "docs" / "guides" / "enterprise-diligence.md",
    ROOT / "docs" / "guides" / "production-readiness.md",
    ROOT / "docs" / "guides" / "performance.md",
    ROOT / "docs" / "guides" / "dashboards.md",
    ROOT / "docs" / "api" / "JINJA.md",
    ROOT / "docs" / "api" / "MOUNT.md",
    ROOT / "docs" / "GLOSSARY.md",
    ROOT / "docs" / "CONTRIBUTING.md",
]

# Patterns that indicate stale "current train" claims (not historical mentions).
STALE = [
    re.compile(r"current published train[^\n]*0\.16", re.I),
    re.compile(r"current published train[^\n]*0\.17", re.I),
    re.compile(r"current published train[^\n]*0\.18", re.I),
    re.compile(r"current published train[^\n]*0\.19", re.I),
    re.compile(r"current published train[^\n]*0\.20", re.I),
    re.compile(r"current published train[^\n]*0\.21", re.I),
    re.compile(r"train is \*\*0\.16\.x\*\*", re.I),
    re.compile(r"latest published train is \*\*0\.16", re.I),
    re.compile(r"Expect \*\*`0\.17\.0`\*\*", re.I),
    re.compile(r"Expect \*\*`0\.18\.0`\*\*", re.I),
    re.compile(r"Expect \*\*`0\.19\.0`\*\*", re.I),
    re.compile(r"Expect \*\*`0\.20\.0`\*\*", re.I),
    re.compile(r"matching `0\.16\.x` pin", re.I),
    re.compile(r"matching `0\.18\.x` pin", re.I),
    re.compile(r"matching `0\.19\.x` pin", re.I),
    re.compile(r"matching `0\.20\.x` pin", re.I),
    re.compile(r"hedron==0\.17\.0", re.I),
    re.compile(r"verify_pkg_15\.py", re.I),
    re.compile(r"hedron>=0\.17\.0", re.I),
    re.compile(r"hedron>=0\.19\.0,<0\.20", re.I),
    re.compile(r"hedron>=0\.20\.0,<0\.21", re.I),
    re.compile(r"capture UI remains Deferred", re.I),
    re.compile(r"Supported lines: \*\*`0\.16\.x`", re.I),
    re.compile(r"Supported lines: \*\*`0\.18\.x`", re.I),
    re.compile(r"Supported lines: \*\*`0\.19\.x`", re.I),
    re.compile(r"Supported lines: \*\*`0\.20\.x`", re.I),
    re.compile(r"Current train — 0\.18", re.I),
    re.compile(r"Current train — 0\.19", re.I),
    re.compile(r"Current train — 0\.20", re.I),
    re.compile(r"Current train: \*\*0\.18", re.I),
    re.compile(r"Current train: \*\*0\.19", re.I),
    re.compile(r"Current train: \*\*0\.20", re.I),
    re.compile(r"Coordinated train: \*\*`0\.18", re.I),
    re.compile(r"Coordinated train: \*\*`0\.19", re.I),
    re.compile(r"Coordinated train: \*\*`0\.20", re.I),
    re.compile(r"Python-first UI framework · v0\.18", re.I),
    re.compile(r"Python-first UI framework · v0\.19", re.I),
    re.compile(r"Python-first UI framework · v0\.20", re.I),
    re.compile(r"Python-first UI framework · Ready to cut 0\.19", re.I),
    re.compile(r"Python-first UI framework · Ready to cut 0\.20", re.I),
    re.compile(r"Python-first UI framework · Ready to cut 0\.21", re.I),
    re.compile(r"Ready to cut: <strong>Hedron 0\.19\.0</strong>", re.I),
    re.compile(r"Ready to cut: <strong>Hedron 0\.20\.0</strong>", re.I),
    re.compile(r"Ready to cut: <strong>Hedron 0\.21\.0</strong>", re.I),
    re.compile(r"current train \(0\.19\)", re.I),
    re.compile(r"current train \(0\.20\)", re.I),
    re.compile(r"Until `v0\.19\.0` is tagged", re.I),
    re.compile(r"Until `v0\.20\.0` is tagged", re.I),
    re.compile(r"Until `v0\.21\.0` is tagged", re.I),
    re.compile(r"Ready to cut on `main` as `0\.19\.0`", re.I),
    re.compile(r"Ready to cut on `main` as `0\.20\.0`", re.I),
    re.compile(r"Ready to cut on `main` as `0\.21\.0`", re.I),
    re.compile(r"Ready to cut on `main`", re.I),
    re.compile(r"Ready-to-cut", re.I),
    re.compile(r"Ready to cut / Implemented", re.I),
    re.compile(r"expects \*\*0\.19\*\*", re.I),
    re.compile(r"expects \*\*0\.20\*\*", re.I),
    re.compile(r"Pin the \*\*0\.18 train\*\*", re.I),
    re.compile(r"Pin the \*\*0\.19 train\*\*", re.I),
    re.compile(r"Pin the \*\*0\.20 train\*\*", re.I),
    re.compile(r"expects \*\*0\.18\*\*", re.I),
    re.compile(r"Cut-ready:\s*<strong>Hedron 0\.6\.0</strong>", re.I),
    re.compile(r"Hedron \*\*0\.18\*\* packages", re.I),
    re.compile(r"Hedron \*\*0\.19\*\* packages", re.I),
    re.compile(r"Hedron \*\*0\.20\*\* packages", re.I),
    re.compile(r"scaffold on \*\*0\.18\.x\*\*", re.I),
    re.compile(r"scaffold on \*\*0\.19\.x\*\*", re.I),
    re.compile(r"scaffold on \*\*0\.20\.x\*\*", re.I),
    re.compile(r"adapter depth on 0\.18\)", re.I),
    re.compile(r"InteractionResult` on \*\*0\.18\.x\*\*", re.I),
    re.compile(r"hedron-charts==0\.1\.0", re.I),
    # Stale "last published is still 0.18/0.19/0.20" claims after v0.21.0 docs flip.
    re.compile(r"last published PyPI/git = `v0\.18\.0`", re.I),
    re.compile(r"last published PyPI/git = `v0\.19\.0`", re.I),
    re.compile(r"last published PyPI/git = `v0\.20\.0`", re.I),
    re.compile(r"last published PyPI/git is `v0\.18\.0`", re.I),
    re.compile(r"last published PyPI/git is `v0\.19\.0`", re.I),
    re.compile(r"last published PyPI/git is `v0\.20\.0`", re.I),
    re.compile(r"hedron==0\.18\.0", re.I),
    re.compile(r"hedron==0\.19\.0", re.I),
    re.compile(r"hedron==0\.20\.0", re.I),
    re.compile(r"current:\s*\*\*`verify_pkg_20\.py`\*\*", re.I),
    re.compile(r"uv run python scripts/verify_pkg_20\.py", re.I),
    re.compile(r"Living train: \*\*0\.20\.0\*\*", re.I),
    re.compile(r"living train \*\*0\.20\*\*", re.I),
    re.compile(r"current train \*\*0\.20\.0\*\*", re.I),
    re.compile(r"current train \*\*0\.20\*\*", re.I),
    re.compile(r"\*\*0\.20 train\*\* \(\*\*Published\*\* as \*\*v0\.20\.0\*\*\)", re.I),
    re.compile(r"kept current with the \*\*0\.20\.0\*\* train", re.I),
    re.compile(r"\*\*Train:\*\* `0\.20\.0`", re.I),
    re.compile(r"Last published: <strong>v0\.18\.0</strong>", re.I),
    re.compile(r"Last published: <strong>v0\.19\.0</strong>", re.I),
    re.compile(r"Last published: <strong>v0\.20\.0</strong>", re.I),
    re.compile(r"PyPI(?:/git)? still serve[s]? \*\*`v0\.18\.0`\*\*", re.I),
    re.compile(r"PyPI(?:/git)? still serve[s]? \*\*`v0\.19\.0`\*\*", re.I),
    re.compile(r"PyPI(?:/git)? still serve[s]? \*\*`v0\.20\.0`\*\*", re.I),
    re.compile(r"\*\*Last published train:\*\* `v0\.18\.0`", re.I),
    re.compile(r"\*\*Last published train:\*\* `v0\.19\.0`", re.I),
    re.compile(r"\*\*Last published train:\*\* `v0\.20\.0`", re.I),
    re.compile(r"current published[^\n]*`v0\.18\.0`", re.I),
    re.compile(r"current published[^\n]*`v0\.19\.0`", re.I),
    re.compile(r"current published[^\n]*`v0\.20\.0`", re.I),
    re.compile(r"Last \*\*published\*\* PyPI train is \*\*0\.18", re.I),
    re.compile(r"Last \*\*published\*\* PyPI train is \*\*0\.19", re.I),
    re.compile(r"Last \*\*published\*\* PyPI train is \*\*0\.20", re.I),
    re.compile(r"0\.19\.x` \| Ready to cut / Implemented on `main` \(not yet published\)", re.I),
    re.compile(r"0\.20\.x` \| Ready to cut / Implemented on `main` \(not yet published\)", re.I),
    re.compile(r"0\.21\.x` \| Ready to cut / Implemented on `main` \(not yet published\)", re.I),
    re.compile(r"superseded before a public `v0\.19\.0` tag", re.I),
    re.compile(r"before a public `v0\.19\.0` tag", re.I),
    re.compile(r"before a public `v0\.20\.0` tag", re.I),
    re.compile(r"before a public `v0\.21\.0` tag", re.I),
    re.compile(r"do \*\*not\*\* treat `0\.20\.0` as published", re.I),
    re.compile(r"Do not treat `0\.20\.0` as published", re.I),
    re.compile(r"do \*\*not\*\* treat `0\.21\.0` as published", re.I),
    re.compile(r"Do not treat `0\.21\.0` as published", re.I),
    re.compile(r"wait for the cut", re.I),
    re.compile(r"after `v0\.20\.0` is tagged", re.I),
    re.compile(r"after\s*\n?\s*`v0\.20\.0` is tagged", re.I),
    re.compile(r"after `v0\.21\.0` is tagged", re.I),
    re.compile(r"Living published train remains \*\*0\.20\*\*", re.I),
    re.compile(r"living published train remains \*\*0\.20\*\*", re.I),
    # Stale "current train is still 0.15–0.20" claims after v0.21.0 docs flip.
    re.compile(r"Current published train is \*\*0\.(?:1[5-9]|20)\*\*", re.I),
    re.compile(r"There is no `hedron new --flask`", re.I),
    re.compile(r"Supported on the 0\.18 train", re.I),
    re.compile(r"guidance for the \*\*0\.19\*\* train", re.I),
    re.compile(r"guidance for the \*\*0\.20\*\* train", re.I),
    # Stale "current train is still 0.21" claims after v0.22.0 docs flip.
    re.compile(r"last published PyPI/git = `v0\.21\.0`", re.I),
    re.compile(r"last published PyPI/git is `v0\.21\.0`", re.I),
    re.compile(r"hedron==0\.21\.0", re.I),
    re.compile(r"current:\s*\*\*`verify_pkg_21\.py`\*\*", re.I),
    re.compile(r"Living train: \*\*0\.21\.0\*\*", re.I),
    re.compile(r"living train \*\*0\.21\*\*", re.I),
    re.compile(r"current train \*\*0\.21\.0\*\*", re.I),
    re.compile(r"current train \*\*0\.21\*\*", re.I),
    re.compile(r"\*\*0\.21 train\*\* \(\*\*Published\*\* as \*\*v0\.21\.0\*\*\)", re.I),
    re.compile(r"kept current with the \*\*0\.21\.0\*\* train", re.I),
    re.compile(r"\*\*Train:\*\* `0\.21\.0`", re.I),
    re.compile(r"Last published: <strong>v0\.21\.0</strong>", re.I),
    re.compile(r"PyPI(?:/git)? still serve[s]? \*\*`v0\.21\.0`\*\*", re.I),
    re.compile(r"\*\*Last published train:\*\* `v0\.21\.0`", re.I),
    re.compile(r"current published[^\n]*`v0\.21\.0`", re.I),
    re.compile(r"Last \*\*published\*\* PyPI train is \*\*0\.21", re.I),
    re.compile(r"Current published train is \*\*0\.21\*\*", re.I),
    re.compile(r"Living published train remains \*\*0\.21\*\*", re.I),
    re.compile(r"living published train remains \*\*0\.21\*\*", re.I),
    re.compile(r"Living published train is \*\*0\.21\*\*", re.I),
    re.compile(r"0\.22 Planned", re.I),
    re.compile(r"CSRF composition \(0\.22 Planned\)", re.I),
    re.compile(r"scaffold on \*\*0\.21\.x\*\*", re.I),
    re.compile(r"Supported lines: \*\*`0\.21\.x`", re.I),
    re.compile(
        r"current published — `v0\.22\.0`\)\*\*\. See", re.I
    ),  # hybrid 0.21+v0.22 in SECURITY
    re.compile(r"`0\.21\.x` \(current published", re.I),
    re.compile(r"matching `0\.21\.x` pin", re.I),
    re.compile(r"current train is \*\*0\.21", re.I),
    re.compile(r"Expect \*\*`0\.22\.0`\*\* \(or a newer `0\.21", re.I),
    re.compile(r"uv run python scripts/verify_pkg_21\.py", re.I),
    re.compile(r"Package verify \(0\.21\)", re.I),
    re.compile(r"hedron&gt;=0\.22\.0,&lt;0\.22", re.I),
    re.compile(r"hedron>=0\.22\.0,<0\.22(?!\d)", re.I),
    re.compile(r"Next: <strong>0\.22</strong>", re.I),
    re.compile(r"living \*\*0\.21\*\* train", re.I),
    re.compile(r"living \*\*0\.20\*\* train", re.I),
    re.compile(r"on the \*\*0\.21\*\* train", re.I),
    re.compile(r"Published as `0\.21\.0`", re.I),
    re.compile(r"last published PyPI = `0\.21\.0`", re.I),
    re.compile(r"Hedron \*\*0\.21\.0\*\*", re.I),
    re.compile(r"\(0\.21 train — \*\*Published\*\*", re.I),
    re.compile(r"git push origin v0\.21\.0", re.I),
    re.compile(r'-m "Hedron 0\.21\.0"', re.I),
    re.compile(r"CSRF composition → 0\.22", re.I),
    re.compile(r"train is \*\*0\.21\.x\*\*", re.I),
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
    r">=0\.22\.0"
    r"(?!,?\s*<0\.23)"
)

BARE_EXTRA = re.compile(r"""["']hedron\[[^\]]+\]["'](?!\s*>=)""")

UNBOUNDED_ALPHA = re.compile(
    r"hedron(?:-charts)?\[(?:charts|notebook|mcp|gradio|native|matplotlib|plotly|altair)\]"
    r">=0\.1\.0(?!,?\s*<0\.2)"
)
UNBOUNDED_CHARTS_PKG = re.compile(r"hedron-charts(?:\[[^\]]+\])?>=0\.1\.0(?!,?\s*<0\.2)")
# pip install "hedron-charts[…]" without a version pin (table mentions are allowed).
UNBOUNDED_CHARTS_INSTALL = re.compile(
    r"""pip\s+install\s+["']hedron-charts(?:\[[^\]]+\])?["'](?!\s*>=)"""
)

PIN_SCAN_ROOTS = [
    ROOT / "docs" / "getting-started",
    ROOT / "docs" / "guides",
    ROOT / "docs" / "examples",
    ROOT / "docs" / "api",
    ROOT / "docs" / "components",
    ROOT / "docs" / "packages",
    ROOT / "docs" / "index.md",
    ROOT / "README.md",
    ROOT / "packages" / "hedron" / "README.md",
    ROOT / "packages" / "hedron-conformance" / "README.md",
    ROOT / "docs" / "packages" / "hedron-extras.md",
    ROOT / "scripts" / "README.md",
    ROOT / "docs" / "CONTRIBUTING.md",
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
                    f"{path.relative_to(ROOT)}:{lineno}: unbounded 0.22 pin "
                    f"(use >=0.22.0,<0.23): {line.strip()[:120]}"
                )
            if BARE_EXTRA.search(line):
                failures.append(
                    f"{path.relative_to(ROOT)}:{lineno}: bare hedron[extra] "
                    f"(add >=…,<… pin): {line.strip()[:120]}"
                )
            if UNBOUNDED_ALPHA.search(line) or UNBOUNDED_CHARTS_PKG.search(line):
                failures.append(
                    f"{path.relative_to(ROOT)}:{lineno}: unbounded Alpha pin "
                    f"(use >=0.1.0,<0.2): {line.strip()[:120]}"
                )
            if UNBOUNDED_CHARTS_INSTALL.search(line):
                failures.append(
                    f"{path.relative_to(ROOT)}:{lineno}: unbounded hedron-charts install "
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
                failures.append(f"{path.relative_to(ROOT)}: stale train claim / {pattern.pattern}")
        for pattern in BANNED:
            if pattern.search(text):
                failures.append(f"{path.relative_to(ROOT)}: banned jargon / {pattern.pattern}")
    failures.extend(_check_unbounded_pins())
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(
        "ok: adopter docs assert Published 0.22 (v0.22.0), "
        "upper-bound pins, and avoid Supported beta / SSOT / beachhead jargon"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
