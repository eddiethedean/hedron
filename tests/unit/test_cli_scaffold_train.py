"""Scaffold train pin must stay aligned with docs/release.toml and the release checker."""

from __future__ import annotations

import importlib.util
import tomllib
from pathlib import Path

import pytest

from hedron.cli import _release_pin_bounds, _scaffold_dep, main

ROOT = Path(__file__).resolve().parents[2]
RELEASE = tomllib.loads((ROOT / "docs/release.toml").read_text(encoding="utf-8"))["release"]


def _load_published_quickstart():
    path = ROOT / "scripts" / "check_published_quickstart.py"
    spec = importlib.util.spec_from_file_location("check_published_quickstart", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("flag", "packages"),
    [
        (None, ("hedron",)),
        ("--flask", ("hedron-flask", "hedron-core")),
        ("--django", ("hedron-django", "hedron-core")),
    ],
)
def test_new_scaffolds_pin_the_documented_train(
    tmp_path: Path,
    flag: str | None,
    packages: tuple[str, ...],
) -> None:
    destination = tmp_path / "app"
    args = ["new", "app", "--path", str(destination)]
    if flag:
        args.append(flag)

    with pytest.raises(SystemExit) as result:
        main(args)

    assert result.value.code == 0
    pyproject = tomllib.loads((destination / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = pyproject["project"]["dependencies"]
    expected_range = f">={RELEASE['pin_floor']},<{RELEASE['pin_ceiling']}"
    for package in packages:
        assert f"{package}{expected_range}" in dependencies


def test_scaffold_helper_matches_release_toml() -> None:
    floor, ceiling = _release_pin_bounds()
    assert floor == RELEASE["pin_floor"]
    assert ceiling == RELEASE["pin_ceiling"]
    assert _scaffold_dep("hedron") == f"hedron>={floor},<{ceiling}"


def test_published_quickstart_pin_matches_scaffold_and_release_toml() -> None:
    """Release CI must not reintroduce the train-.0 pin that failed v0.28.1."""
    module = _load_published_quickstart()
    version = RELEASE["published_version"]
    expected = module.expected_hedron_scaffold_pin(version)
    assert expected == f">={RELEASE['pin_floor']},<{RELEASE['pin_ceiling']}"
    assert f"hedron{expected}" == _scaffold_dep("hedron")
    if not version.endswith(".0"):
        train = ".".join(version.split(".")[:2])
        assert expected != f">={train}.0,<{RELEASE['pin_ceiling']}"
