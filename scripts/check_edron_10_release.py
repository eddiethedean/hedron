#!/usr/bin/env python3
"""Validate Edron 1.0 artifacts on the Hedron 1.0 train."""

from __future__ import annotations

import argparse
import sys
import tarfile
import zipfile
from pathlib import Path

from check_edron_release import _fail, _project_version, check_artifacts

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
CURRENT_VERSION = "1.0.0"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--version", default=CURRENT_VERSION)
    args = parser.parse_args(argv)
    try:
        version = _project_version()
        if version != CURRENT_VERSION or args.version != version:
            _fail(f"expected Edron {CURRENT_VERSION}, found {version}")
        check_artifacts(args.dist_dir, version)
    except (
        OSError,
        ValueError,
        tarfile.TarError,
        tomllib.TOMLDecodeError,
        zipfile.BadZipFile,
    ) as exc:
        print(f"Edron 1.0 release check failed: {exc}", file=sys.stderr)
        return 1
    print("Edron 1.0.0 release artifacts are valid on Hedron 1.x")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
