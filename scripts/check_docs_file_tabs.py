#!/usr/bin/env python3
"""Validate the file-tab convention for public multi-file documentation examples."""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
_FILE = r"[^\"]+\.(?:py|css|toml|html|jinja|hdj|mjs|js|json|ya?ml|txt|md)"
_TAB = re.compile(rf'^=== "(?P<path>{_FILE})"\s*$')
_FENCE = re.compile(r'^\s+```[A-Za-z0-9_+-]+\s+title="(?P<path>[^"]+)"\s*$')
_HEADING = re.compile(r"^##\s+(?P<title>.+?)\s*$")
_FULL_CODE_LINK = re.compile(
    r"\[Full code on GitHub\]\("
    r"https://github\.com/eddiethedean/hedron/"
    r"(?P<kind>tree|blob)/main/(?P<target>[^)]+)"
    r"\)"
)
_TOP_LEVEL_FENCE = re.compile(r"^(?P<marker>`{3,}|~{3,})")

_REQUIRED: dict[str, set[str]] = {
    "examples/composable-app.md": {
        "app.py",
        "components/__init__.py",
        "components/activity.py",
        "components/deployments.py",
        "components/metrics.py",
        "components/status.py",
        "custom_css.py",
        "styles.css",
        "pyproject.toml",
    },
    "guides/plugin-authoring.md": {
        "pyproject.toml",
        "src/my_hedron_plugin/plugin.py",
    },
    "guides/styling.md": {
        "components/Callout/component.py",
        "components/Callout/styles.css",
    },
    "api/PLUGINS.md": {
        "pyproject.toml",
        "src/hedron_sample_kit/plugin.py",
    },
    "packages/hedron-sample-kit.md": {"pyproject.toml", "app.py"},
    "getting-started/coding-agents.md": {"app.py", "test_app.py"},
}


def _check(path: Path) -> tuple[set[str], list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    labels: set[str] = set()
    errors: list[str] = []
    section = "<document>"
    section_tabs: dict[str, list[str]] = defaultdict(list)
    section_source_links: set[str] = set()
    block_fence: str | None = None

    for index, line in enumerate(lines):
        fence_marker = _TOP_LEVEL_FENCE.match(line)
        if block_fence is not None:
            if (
                fence_marker is not None
                and fence_marker.group("marker")[0] == block_fence[0]
                and len(fence_marker.group("marker")) >= len(block_fence)
            ):
                block_fence = None
            continue
        if fence_marker is not None:
            block_fence = fence_marker.group("marker")
            continue
        heading = _HEADING.match(line)
        if heading is not None:
            section = heading.group("title")
        source_link = _FULL_CODE_LINK.search(line)
        if source_link is not None:
            section_source_links.add(section)
            target = ROOT / source_link.group("target")
            if not target.exists():
                errors.append(
                    f"{path.relative_to(ROOT)}:{index + 1}: Full code on GitHub "
                    f"target does not exist: {target.relative_to(ROOT)}"
                )
            elif source_link.group("kind") == "tree" and not target.is_dir():
                errors.append(
                    f"{path.relative_to(ROOT)}:{index + 1}: GitHub tree link must "
                    f"target a directory: {target.relative_to(ROOT)}"
                )
            elif source_link.group("kind") == "blob" and not target.is_file():
                errors.append(
                    f"{path.relative_to(ROOT)}:{index + 1}: GitHub blob link must "
                    f"target a file: {target.relative_to(ROOT)}"
                )
        tab = _TAB.match(line)
        if tab is None:
            continue
        label = tab.group("path")
        labels.add(label)
        section_tabs[section].append(label)
        cursor = index + 1
        while cursor < len(lines) and not lines[cursor].strip():
            cursor += 1
        fence = _FENCE.match(lines[cursor]) if cursor < len(lines) else None
        if fence is None:
            errors.append(
                f"{path.relative_to(ROOT)}:{index + 1}: file tab has no titled code fence"
            )
        elif fence.group("path") != label:
            errors.append(
                f"{path.relative_to(ROOT)}:{index + 1}: tab {label!r} does not match "
                f"fence title {fence.group('path')!r}"
            )

    for title, tabs in section_tabs.items():
        if len(tabs) == 1:
            errors.append(
                f"{path.relative_to(ROOT)}: section {title!r} has one file tab; "
                "keep one-file examples linear or add the other coexisting files"
            )
        elif len(tabs) >= 2 and title not in section_source_links:
            errors.append(
                f"{path.relative_to(ROOT)}: section {title!r} has multiple file tabs "
                "but no Full code on GitHub link"
            )
    return labels, errors


def main() -> int:
    failed: list[str] = []
    labels_by_path: dict[str, set[str]] = {}
    for path in sorted(DOCS.rglob("*.md")):
        labels, errors = _check(path)
        labels_by_path[path.relative_to(DOCS).as_posix()] = labels
        failed.extend(errors)

    for relative, required in _REQUIRED.items():
        missing = sorted(required - labels_by_path.get(relative, set()))
        if missing:
            failed.append(f"docs/{relative}: missing required file tabs: {', '.join(missing)}")

    if failed:
        for message in failed:
            print(message, file=sys.stderr)
        return 1
    print("ok: public multi-file examples use matching file tabs and GitHub source links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
