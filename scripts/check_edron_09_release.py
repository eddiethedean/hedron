#!/usr/bin/env python3
"""Validate Edron 0.9 artifacts on the Hedron 0.67.0 train."""

from __future__ import annotations

import argparse
import sys
import tarfile
import tomllib
import zipfile
from pathlib import Path

from check_edron_release import _fail, _project_version, check_artifacts

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--version", default="0.9.0")
    args = parser.parse_args(argv)
    try:
        version = _project_version()
        if version != "0.9.0" or args.version != version:
            _fail(f"expected Edron 0.9.0, found {version}")
        check_artifacts(args.dist_dir, version)
    except (
        OSError,
        ValueError,
        tarfile.TarError,
        tomllib.TOMLDecodeError,
        zipfile.BadZipFile,
    ) as exc:
        print(f"Edron 0.9 release check failed: {exc}", file=sys.stderr)
        return 1
    print("Edron 0.9.0 release artifacts are valid on Hedron 0.67.0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
