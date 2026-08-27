"""Scaffold train pin must stay aligned with docs/release.toml and the release checker."""

from __future__ import annotations

import importlib.util
import tomllib
from argparse import Namespace
from pathlib import Path

import pytest

from hedron.cli import _cmd_run_app, _release_pin_bounds, _scaffold_dep, main

ROOT = Path(__file__).resolve().parents[2]
RELEASE = tomllib.loads((ROOT / "docs/release.toml").read_text(encoding="utf-8"))["release"]


def _load_published_quickstart():
    path = ROOT / "scripts" / "check_published_quickstart.py"
    spec = importlib.util.spec_from_file_location("check_published_quickstart", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _scaffold_floor_ceiling() -> tuple[str, str]:
    if RELEASE.get("registry_status") == "deferred":
        return str(RELEASE["pypi_pin_floor"]), str(RELEASE["pypi_pin_ceiling"])
    return str(RELEASE["pin_floor"]), str(RELEASE["pin_ceiling"])


def _scaffold_pin_range() -> str:
    floor, ceiling = _scaffold_floor_ceiling()
    return f">={floor},<{ceiling}"


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
    expected_range = _scaffold_pin_range()
    for package in packages:
        assert f"{package}{expected_range}" in dependencies


def test_scaffold_helper_matches_release_toml() -> None:
    floor, ceiling = _release_pin_bounds()
    expected_floor, expected_ceiling = _scaffold_floor_ceiling()
    assert floor == expected_floor
    assert ceiling == expected_ceiling
    assert _scaffold_dep("hedron") == f"hedron>={floor},<{ceiling}"


def test_published_quickstart_pin_matches_scaffold_and_release_toml() -> None:
    """Release CI must not reintroduce the train-.0 pin that failed v0.28.1."""
    module = _load_published_quickstart()
    version = RELEASE["published_version"]
    in_tree = module.expected_hedron_scaffold_pin(version)
    assert in_tree == f">={RELEASE['pin_floor']},<{RELEASE['pin_ceiling']}"
    scaffold = _scaffold_dep("hedron")
    if RELEASE.get("registry_status") == "deferred":
        assert scaffold == f"hedron>={RELEASE['pypi_pin_floor']},<{RELEASE['pypi_pin_ceiling']}"
        assert f"hedron{in_tree}" != scaffold
    else:
        assert f"hedron{in_tree}" == scaffold
    if not version.endswith(".0"):
        train = ".".join(version.split(".")[:2])
        assert in_tree != f">={train}.0,<{RELEASE['pin_ceiling']}"


@pytest.mark.parametrize(
    ("version", "expected"),
    [
        ("0.64.1", ">=0.64.1,<0.65"),
        ("0.65.0", ">=0.65.0,<0.66"),
        ("1.2.3", ">=1.2.3,<1.3"),
    ],
)
def test_published_quickstart_pin_is_derived_from_artifact_version(
    version: str, expected: str
) -> None:
    """Patch, minor, and future major releases do not depend on stale docs metadata."""
    module = _load_published_quickstart()
    assert module.expected_hedron_scaffold_pin(version) == expected


def test_published_quickstart_matches_current_development_artifact() -> None:
    """The next tag's verifier contract is exercised on every ordinary test run."""
    module = _load_published_quickstart()
    version = str(RELEASE["development_version"])
    major, minor, _patch = (int(part) for part in version.split("."))
    assert module.expected_hedron_scaffold_pin(version) == f">={version},<{major}.{minor + 1}"


def test_published_quickstart_finds_exact_local_wheels(tmp_path: Path) -> None:
    module = _load_published_quickstart()
    expected = tmp_path / "hedron_core-0.65.0-py3-none-any.whl"
    expected.touch()
    (tmp_path / "hedron_core-0.64.1-py3-none-any.whl").touch()

    assert module.find_wheel(tmp_path, "hedron-core", "0.65.0") == expected.resolve()


def test_hedron_run_auto_delegates_to_workbench_launcher(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called: dict[str, object] = {}

    def fake_run(target: str, *, config: object) -> None:
        called.update(target=target, config=config)

    monkeypatch.setenv("RS_SERVER_URL", "https://wb.example/s/session/")
    monkeypatch.setattr("hedron_posit.runner.run_target", fake_run)
    args = Namespace(
        target="sample:app",
        app=None,
        workbench=False,
        workbench_mode="auto",
        host=None,
        port=None,
        mount=None,
        public_base_url=None,
        forwarded_allow_ips=None,
        allow_external_bind=False,
        reload=False,
        workers=1,
        debug=False,
        factory=False,
        topology="auto",
    )
    assert _cmd_run_app(args) == 0
    assert called["target"] == "sample:app"
