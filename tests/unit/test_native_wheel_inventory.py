"""Tests for the candidate native wheel matrix inventory."""

from __future__ import annotations

from pathlib import Path

import pytest
from packaging.version import Version

from scripts import verify_native_wheel_inventory as inventory

PLATFORM_WHEEL_TAGS = {
    "linux-x86_64": "manylinux_2_17_x86_64",
    "linux-aarch64": "manylinux_2_17_aarch64",
    "macos-arm64": "macosx_11_0_arm64",
    "windows-amd64": "win_amd64",
}


def create_wheels(wheel_dir: Path, platform_tags: dict[str, str] | None = None) -> None:
    tags = platform_tags or PLATFORM_WHEEL_TAGS
    for platform_tag in tags.values():
        for python_tag in inventory.PYTHON_TAGS:
            (
                wheel_dir / f"hedron_native-0.1.4-{python_tag}-{python_tag}-{platform_tag}.whl"
            ).touch()


@pytest.mark.parametrize("platform_name,platform_tag", PLATFORM_WHEEL_TAGS.items())
def test_platform_inventory_requires_all_four_supported_interpreters(
    tmp_path: Path, platform_name: str, platform_tag: str
) -> None:
    wheel_dir = tmp_path / "wheels"
    wheel_dir.mkdir()
    for python_tag in inventory.PYTHON_TAGS:
        (wheel_dir / f"hedron_native-0.1.4-{python_tag}-{python_tag}-{platform_tag}.whl").touch()

    result = inventory.collect_inventory(
        wheel_dir, platform_name=platform_name, version=Version("0.1.4")
    )

    assert result["platform"] == platform_name
    assert len(result["wheels"]) == 4


def test_platform_inventory_rejects_a_missing_python_314_wheel(tmp_path: Path) -> None:
    wheel_dir = tmp_path / "wheels"
    wheel_dir.mkdir()
    for python_tag in inventory.PYTHON_TAGS[:-1]:
        (wheel_dir / f"hedron_native-0.1.4-{python_tag}-{python_tag}-win_amd64.whl").touch()

    with pytest.raises(ValueError, match="matrix incomplete"):
        inventory.collect_inventory(
            wheel_dir, platform_name="windows-amd64", version=Version("0.1.4")
        )


def test_platform_inventory_rejects_python_310_wheels(tmp_path: Path) -> None:
    wheel_dir = tmp_path / "wheels"
    wheel_dir.mkdir()
    for python_tag in ("cp310", *inventory.PYTHON_TAGS[1:]):
        (wheel_dir / f"hedron_native-0.1.4-{python_tag}-{python_tag}-win_amd64.whl").touch()

    with pytest.raises(ValueError, match="outside the supported CPython wheel matrix"):
        inventory.collect_inventory(
            wheel_dir, platform_name="windows-amd64", version=Version("0.1.4")
        )


def test_combined_inventory_requires_every_declared_platform(tmp_path: Path) -> None:
    create_wheels(tmp_path, {"linux-x86_64": PLATFORM_WHEEL_TAGS["linux-x86_64"]})

    with pytest.raises(ValueError, match="matrix incomplete"):
        inventory.collect_inventory(tmp_path, platform_name=None, version=Version("0.1.4"))


def test_combined_inventory_accepts_all_sixteen_candidate_wheels(tmp_path: Path) -> None:
    create_wheels(tmp_path)

    result = inventory.collect_inventory(tmp_path, platform_name=None, version=Version("0.1.4"))

    assert set(result["platforms"]) == set(PLATFORM_WHEEL_TAGS)
    assert sum(len(wheels) for wheels in result["platforms"].values()) == 16
