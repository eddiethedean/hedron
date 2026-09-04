#!/usr/bin/env python3
"""Require a package version bump whenever a package payload changes.

This check is intentionally based on the pull request diff rather than the
registry. It catches a package change before a release is cut, including
changes to static assets that are bundled into a wheel.
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from collections.abc import Iterable
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


def version_change_errors(base: str, head: str) -> list[str]:
    errors: list[str] = []
    package_dirs = sorted(
        {
            Path(path).parts[1]
            for path in changed_paths(base, head)
            if len(Path(path).parts) > 1 and Path(path).parts[0] == "packages"
        }
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
