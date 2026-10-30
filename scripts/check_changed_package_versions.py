#!/usr/bin/env python3
"""Require a package version bump whenever a package payload changes.

This check is intentionally based on the pull request diff rather than the
registry. It catches a package change before a release is cut, including
changes to static assets that are bundled into a wheel.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from collections.abc import Iterable
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git_show(ref: str, path: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout if result.returncode == 0 else None


def changed_paths(base: str, head: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...{head}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [path for path in result.stdout.splitlines() if path]


def project_metadata(text: str) -> tuple[str, str]:
    project = tomllib.loads(text)["project"]
    return str(project["name"]), str(project["version"])


def unreleased_development_version(ref: str) -> tuple[str, str] | None:
    release_text = git_show(ref, "docs/release.toml")
    if release_text is None:
        return None
    release = tomllib.loads(release_text).get("release", {})
    development = release.get("development_version")
    published = release.get("published_version")
    if not isinstance(development, str) or not isinstance(published, str):
        return None
    return development, published


def finalized_changelog_header_only(
    base: str,
    head: str,
    directory: str,
    version: str,
    package_paths: list[str],
) -> bool:
    """Allow closing a published changelog date without a new package release."""
    changelog = f"packages/{directory}/CHANGELOG.md"
    if package_paths != [changelog]:
        return False
    base_text = git_show(base, changelog)
    head_text = git_show(head, changelog)
    if base_text is None or head_text is None:
        return False
    base_lines = base_text.splitlines()
    head_lines = head_text.splitlines()
    expected_unreleased = f"## [{version}] — Unreleased"
    if len(base_lines) < 3 or len(head_lines) < 3:
        return False
    if base_lines[:2] != head_lines[:2] or base_lines[2] != expected_unreleased:
        return False
    match = re.fullmatch(rf"## \[{re.escape(version)}\] — (\d{{4}}-\d{{2}}-\d{{2}})", head_lines[2])
    if match is None or base_lines[3:] != head_lines[3:]:
        return False
    try:
        date.fromisoformat(match.group(1))
    except ValueError:
        return False
    return True


def version_change_errors(base: str, head: str) -> list[str]:
    errors: list[str] = []
    development_versions = unreleased_development_version(head)
    paths_by_package: dict[str, list[str]] = {}
    for path in changed_paths(base, head):
        parts = Path(path).parts
        if len(parts) > 1 and parts[0] == "packages":
            paths_by_package.setdefault(parts[1], []).append(path)
    package_dirs = sorted(
        paths_by_package
    )
    for directory in package_dirs:
        relative = f"packages/{directory}/pyproject.toml"
        head_text = git_show(head, relative)
        if head_text is None:
            # A removed package has no release artifact to publish.
            continue
        head_name, head_version = project_metadata(head_text)
        base_text = git_show(base, relative)
        if base_text is None:
            print(f"ok: new package {head_name} declares version {head_version}")
            continue
        base_name, base_version = project_metadata(base_text)
        if head_name != base_name:
            errors.append(
                f"{relative}: package name changed from {base_name!r} to {head_name!r}; "
                "rename the package explicitly instead of reusing its version"
            )
        elif head_version == base_version:
            if finalized_changelog_header_only(
                base,
                head,
                directory,
                head_version,
                paths_by_package[directory],
            ):
                print(
                    f"ok: {head_name} changelog date finalized for existing version "
                    f"{head_version}"
                )
            elif (
                development_versions is not None
                and head_version == development_versions[0]
                and development_versions[0] != development_versions[1]
            ):
                print(f"ok: {head_name} remains on unreleased development version {head_version}")
            else:
                errors.append(
                    f"{head_name}: package files changed but version stayed at {head_version}; "
                    "bump the package version"
                )
        else:
            print(f"ok: {head_name} changed version {base_version} -> {head_version}")
    return errors


def main(argv: Iterable[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if len(args) != 2:
        print(f"usage: {Path(sys.argv[0]).name} BASE_SHA HEAD_SHA", file=sys.stderr)
        return 2
    try:
        errors = version_change_errors(args[0], args[1])
    except (OSError, subprocess.CalledProcessError, tomllib.TOMLDecodeError) as exc:
        print(f"package version change check failed: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ok: every changed package has a version change")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
