from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from hedron.cli import main

ROOT = Path(__file__).resolve().parents[2]
RELEASE = tomllib.loads((ROOT / "docs/release.toml").read_text(encoding="utf-8"))["release"]


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
