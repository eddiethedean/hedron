#!/usr/bin/env python3
"""Validate and print the deterministic PyPI publication order."""

from __future__ import annotations

from pathlib import Path

from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
ORDER_PATH = ROOT / "release" / "publish-order.toml"


def workspace_projects() -> dict[str, tuple[str, tuple[str, ...]]]:
    projects: dict[str, tuple[str, tuple[str, ...]]] = {}
    for project_file in sorted((ROOT / "packages").glob("*/pyproject.toml")):
        project = tomllib.loads(project_file.read_text(encoding="utf-8"))["project"]
        name = str(project["name"])
        dependencies: list[str] = []
        for raw in project.get("dependencies", []):
            try:
                dependencies.append(canonicalize_name(Requirement(str(raw)).name))
            except InvalidRequirement as exc:
                raise SystemExit(f"{name}: invalid dependency requirement {raw!r}: {exc}") from exc
        projects[canonicalize_name(name)] = (name, tuple(dependencies))
    return projects


def dependency_order_errors(
    order: list[str],
    excluded: list[str],
    projects: dict[str, tuple[str, tuple[str, ...]]],
) -> list[str]:
    positions = {canonicalize_name(name): index for index, name in enumerate(order)}
    exclusions = {canonicalize_name(name) for name in excluded}
    errors: list[str] = []
    for project_key, (project_name, dependencies) in projects.items():
        if project_key not in positions:
            continue
        for dependency in dependencies:
            if dependency not in projects:
                continue
            dependency_name = projects[dependency][0]
            if dependency in exclusions:
                errors.append(
                    f"{project_name}: required workspace dependency {dependency_name} is excluded"
                )
            elif positions.get(dependency, len(order)) >= positions[project_key]:
                errors.append(
                    f"{project_name}: required workspace dependency {dependency_name} must be "
                    "published first"
                )
    return errors


def main() -> int:
    data = tomllib.loads(ORDER_PATH.read_text(encoding="utf-8"))
    order = data.get("order")
    excluded = data.get("excluded")
    if not isinstance(order, list) or not all(isinstance(item, str) for item in order):
        raise SystemExit("release publish order must contain a string order list")
    if not isinstance(excluded, list) or not all(isinstance(item, str) for item in excluded):
        raise SystemExit("release publish order must contain a string excluded list")
    if len(order) != len(set(order)) or set(order) & set(excluded):
        raise SystemExit("release publish order contains duplicates or excluded projects")

    projects = workspace_projects()
    workspace_names = {item[0] for item in projects.values()}
    missing = workspace_names - set(order) - set(excluded)
    if missing:
        raise SystemExit(
            "release publish order does not classify workspace projects: "
            + ", ".join(sorted(missing))
        )
    ordering_errors = dependency_order_errors(order, excluded, projects)
    if ordering_errors:
        raise SystemExit("\n".join(ordering_errors))
    for name in order:
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
