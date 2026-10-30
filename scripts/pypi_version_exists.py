#!/usr/bin/env python3
"""Report whether an exact package version already exists on PyPI.

The release workflow runs the full immutable wheel-payload parity check before
using this helper. Existing versions must be skipped as a whole: PyPI rejects
re-uploading an existing filename when only archive/build metadata differs.
"""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request


def version_exists(name: str, version: str) -> bool:
    url = f"https://pypi.org/pypi/{name}/{version}/json"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return False
        raise
    actual = payload.get("info", {}).get("version")
    if actual != version:
        raise ValueError(f"PyPI returned {name}=={actual!r} for requested version {version!r}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name")
    parser.add_argument("version")
    args = parser.parse_args()
    print("present" if version_exists(args.name, args.version) else "absent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
