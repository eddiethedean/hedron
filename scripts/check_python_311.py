#!/usr/bin/env python3
"""Enforce the maintained workspace's CPython 3.11+ baseline."""

from __future__ import annotations

import ast
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_RANGE = ">=3.11,<3.15"
MATRIX = ["3.11", "3.12", "3.13", "3.14"]


def load_project(path: Path) -> dict[str, object]:
    return tomllib.loads(path.read_text(encoding="utf-8"))["project"]


def package_uses_typing_extensions(package: Path) -> bool:
    for source in (package / "src").rglob("*.py"):
        try:
            tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        except (OSError, UnicodeDecodeError, SyntaxError) as exc:
            raise ValueError(f"cannot inspect {source.relative_to(ROOT)}: {exc}") from exc
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "typing_extensions":
                return True
            if isinstance(node, ast.Import) and any(
                alias.name == "typing_extensions" for alias in node.names
            ):
                return True
    return False


def workflow_errors(directory: Path) -> list[str]:
    """Check combined CI coverage and publication's reuse of branch CI."""
    errors: list[str] = []
    ci = (directory / "ci.yml").read_text(encoding="utf-8")
    matrix = re.search(r"python-version: \[([^\]]+)\]", ci)
    versions = set(re.findall(r'"(3\.\d+)"', matrix.group(1))) if matrix else set()
    coverage = re.search(r"^  coverage:\n(.*?)(?=^  \S|\Z)", ci, re.M | re.S)
    if coverage and "scripts/ci_checks.sh coverage --python 3.12" in coverage.group(1):
        versions.add("3.12")
    if versions != set(MATRIX):
        errors.append("CI's test and coverage jobs must cover CPython 3.11–3.14")
    for name in ("release.yml", "edron-release.yml"):
        workflow = (directory / name).read_text(encoding="utf-8")
        if "bash scripts/check_release_ci.sh" not in workflow:
            errors.append(f"{name}: publication must require successful branch CI")
    return errors


def check() -> list[str]:
    errors: list[str] = []
    root_data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    workspace = root_data["project"]
    if workspace.get("requires-python") != PYTHON_RANGE:
        errors.append(f"root requires-python must be {PYTHON_RANGE}")
    ruff = root_data.get("tool", {}).get("ruff", {})
    if ruff.get("target-version") != "py311":
        errors.append("Ruff target-version must be py311")
    pyright = root_data.get("tool", {}).get("basedpyright", {})
    if pyright.get("pythonVersion") != "3.11":
        errors.append("BasedPyright pythonVersion must be 3.11")
    if pyright.get("typeCheckingMode") != "all":
        errors.append("BasedPyright typeCheckingMode must remain all")

    members = root_data.get("tool", {}).get("uv", {}).get("workspace", {}).get("members", [])
    member_names: set[str] = set()
    for member in members:
        package_file = ROOT / str(member) / "pyproject.toml"
        if not package_file.is_file():
            errors.append(f"workspace member is missing: {member}")
            continue
        project = load_project(package_file)
        name = str(project.get("name", member))
        member_names.add(name)
        if project.get("requires-python") != PYTHON_RANGE:
            errors.append(f"{name}: requires-python must be {PYTHON_RANGE}")
        classifiers = project.get("classifiers", [])
        if "Programming Language :: Python :: 3.10" in classifiers:
            errors.append(f"{name}: Python 3.10 classifier must be removed")
        for version in MATRIX:
            classifier = f"Programming Language :: Python :: {version}"
            if classifier not in classifiers:
                errors.append(f"{name}: missing classifier {classifier}")
        dependencies = [str(dep).lower() for dep in project.get("dependencies", [])]
        if any("tomli" in dependency for dependency in dependencies):
            errors.append(f"{name}: direct tomli dependency is obsolete")
        if package_uses_typing_extensions(ROOT / str(member)) and not any(
            dependency.startswith("typing-extensions>=4.10") for dependency in dependencies
        ):
            errors.append(f"{name}: typing_extensions imports require direct >=4.10 dependency")

    expected_members = {
        str(load_project(path).get("name")) for path in (ROOT / "packages").glob("*/pyproject.toml")
    }
    if member_names != expected_members:
        errors.append("uv workspace member inventory does not match packages/*/pyproject.toml")
    if len(member_names) != 23:
        errors.append(f"expected 23 maintained workspace packages, found {len(member_names)}")

    for path in (ROOT / "examples").glob("*/pyproject.toml"):
        example_data = tomllib.loads(path.read_text(encoding="utf-8"))
        project = example_data.get("project")
        if not isinstance(project, dict):
            continue
        if project.get("requires-python") != PYTHON_RANGE:
            errors.append(f"{path.relative_to(ROOT)}: example must require Python {PYTHON_RANGE}")

    support_matrix = tomllib.loads(
        (ROOT / "release" / "support-matrix.toml").read_text(encoding="utf-8")
    )
    if support_matrix.get("release", {}).get("python") != MATRIX:
        errors.append("release/support-matrix.toml must list CPython 3.11 through 3.14")
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    if str(lock.get("requires-python", "")).replace(" ", "") != PYTHON_RANGE:
        errors.append(f"uv.lock requires-python must be {PYTHON_RANGE}")

    errors.extend(workflow_errors(ROOT / ".github" / "workflows"))

    local_ci = (ROOT / "scripts" / "ci_checks.sh").read_text(encoding="utf-8")
    if "CI_PYTHONS=(3.11 3.12 3.13 3.14)" not in local_ci:
        errors.append("scripts/ci_checks.sh must default to CPython 3.11 through 3.14")

    for path in (
        ROOT / ".github" / "workflows" / "native-wheels.yml",
        ROOT / "packages" / "hedron-native" / "pyproject.toml",
    ):
        source = path.read_text(encoding="utf-8")
        if "cp310" in source:
            errors.append(f"{path.relative_to(ROOT)} still builds CPython 3.10 wheels")
        if "cp311" not in source:
            errors.append(f"{path.relative_to(ROOT)} must build CPython 3.11 wheels")

    scaffold_projects = (
        ROOT / "packages" / "hedron" / "src" / "hedron" / "cli" / "scaffold" / "django.py",
        ROOT / "packages" / "hedron" / "src" / "hedron" / "cli" / "scaffold" / "element.py",
        ROOT / "packages" / "hedron" / "src" / "hedron" / "cli" / "scaffold" / "fastapi.py",
        ROOT / "packages" / "hedron" / "src" / "hedron" / "cli" / "scaffold" / "flask.py",
        ROOT / "packages" / "edron" / "src" / "edron" / "scaffolds.py",
    )
    for path in scaffold_projects:
        if f'requires-python = "{PYTHON_RANGE}"' not in path.read_text(encoding="utf-8"):
            errors.append(f"{path.relative_to(ROOT)} scaffold must require Python {PYTHON_RANGE}")

    direct_dependency_files = [
        ROOT / "pyproject.toml",
        ROOT / "release" / "stable-dependencies.txt",
        *sorted((ROOT / "packages").glob("*/pyproject.toml")),
    ]
    for path in direct_dependency_files:
        if re.search(
            r"(?im)^\s*['\"]?tomli(?:[<>=!~;\[]|['\"]|$)",
            path.read_text(encoding="utf-8"),
        ):
            errors.append(f"{path.relative_to(ROOT)} still declares tomli directly")

    if errors:
        return errors
    print(
        "ok: workspace metadata, typing, CI, native wheels, and direct dependencies "
        "target Python 3.11+"
    )
    return []


if __name__ == "__main__":
    failures = check()
    if failures:
        print("\n".join(f"error: {failure}" for failure in failures), file=sys.stderr)
        raise SystemExit(1)
