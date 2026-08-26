#!/usr/bin/env python3
"""Validate the Edron release metadata and built distribution contents."""

from __future__ import annotations

import argparse
import sys
import tarfile
import tomllib
import zipfile
from email.parser import BytesParser
from email.policy import compat32
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "packages" / "edron"
REQUIRED_WHEEL_FILES = {
    "edron/__init__.py",
    "edron/py.typed",
    "edron/diagnostics.py",
    "edron/data.py",
    "edron/scaffolds.py",
    "edron/tooling.py",
    "edron/cli/main.py",
}
REQUIRED_SDIST_SUFFIXES = {
    "/src/edron/__init__.py",
    "/src/edron/py.typed",
    "/src/edron/diagnostics.py",
    "/src/edron/data.py",
    "/src/edron/scaffolds.py",
    "/src/edron/tooling.py",
    "/README.md",
    "/CHANGELOG.md",
    "/LICENSE",
    "/pyproject.toml",
}
FORBIDDEN_WHEEL_PREFIXES = ("hedron/", "hedron_core/", "hedron_data/", "hedron_charts/")


def _fail(message: str) -> None:
    raise ValueError(message)


def _project_version() -> str:
    project = tomllib.loads(
        (PACKAGE / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    version = str(project["version"])
    source = (PACKAGE / "src" / "edron" / "__init__.py").read_text(encoding="utf-8")
    if f'__version__ = "{version}"' not in source:
        _fail(f"packages/edron __version__ does not match {version}")
    changelog = (PACKAGE / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## [{version}]" not in changelog:
        _fail(f"packages/edron/CHANGELOG.md has no [{version}] heading")
    return version


def _metadata(archive: zipfile.ZipFile) -> tuple[str, str]:
    metadata_names = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
    if len(metadata_names) != 1:
        _fail(f"expected one wheel METADATA file, found {metadata_names}")
    message = BytesParser(policy=compat32).parsebytes(archive.read(metadata_names[0]))
    return message.get("Name", ""), message.get("Version", "")


def check_artifacts(dist_dir: Path, expected_version: str) -> None:
    wheels = sorted(dist_dir.glob(f"edron-{expected_version}-*.whl"))
    sdists = sorted(dist_dir.glob(f"edron-{expected_version}.tar.gz"))
    if len(wheels) != 1:
        _fail(f"expected exactly one Edron {expected_version} wheel, found {wheels}")
    if len(sdists) != 1:
        _fail(f"expected exactly one Edron {expected_version} sdist, found {sdists}")

    with zipfile.ZipFile(wheels[0]) as archive:
        names = set(archive.namelist())
        missing = REQUIRED_WHEEL_FILES - names
        if missing:
            _fail(f"wheel is missing required files: {sorted(missing)}")
        copied = [name for name in names if name.startswith(FORBIDDEN_WHEEL_PREFIXES)]
        if copied:
            _fail(f"wheel copied native package files: {sorted(copied)[:5]}")
        name, version = _metadata(archive)
        if (name, version) != ("edron", expected_version):
            _fail(f"wheel metadata is {name} {version}, expected edron {expected_version}")

    with tarfile.open(sdists[0], "r:gz") as archive:
        names = {member.name for member in archive.getmembers()}
        missing = {
            suffix
            for suffix in REQUIRED_SDIST_SUFFIXES
            if not any(name.endswith(suffix) for name in names)
        }
        if missing:
            _fail(f"sdist is missing required files: {sorted(missing)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--version", default=None)
    args = parser.parse_args(argv)
    try:
        version = _project_version()
        if args.version is not None and args.version != version:
            _fail(f"requested version {args.version} does not match package version {version}")
        check_artifacts(args.dist_dir, version)
    except (
        OSError,
        ValueError,
        tarfile.TarError,
        tomllib.TOMLDecodeError,
        zipfile.BadZipFile,
    ) as exc:
        print(f"Edron release check failed: {exc}", file=sys.stderr)
        return 1
    print(f"Edron {version} release artifacts are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
