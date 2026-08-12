#!/usr/bin/env python3
"""Validate a redirect target before a smoke test follows it."""

from __future__ import annotations

import argparse
from urllib.parse import urljoin, urlsplit, urlunsplit

from hedron.mount import normalize_mount_path
from hedron_core.htmx_contract import is_local_path


def safe_redirect_target(*, origin: str, mount: str, location: str) -> str:
    expected = urlsplit(origin)
    if expected.scheme not in {"http", "https"} or not expected.netloc:
        raise ValueError("expected origin must be an absolute http(s) URL")
    if expected.path not in {"", "/"} or expected.query or expected.fragment:
        raise ValueError("expected origin must not contain a path, query, or fragment")

    raw = str(location).strip()
    if not raw or "\\" in raw or any(ord(char) < 32 for char in raw):
        raise ValueError("redirect Location is empty or contains unsafe characters")
    absolute = urlsplit(urljoin(urlunsplit(expected), raw))
    if (absolute.scheme.lower(), absolute.netloc.lower()) != (
        expected.scheme.lower(),
        expected.netloc.lower(),
    ):
        raise ValueError("redirect changed origin")
    if absolute.username is not None or absolute.password is not None or absolute.fragment:
        raise ValueError("redirect contains credentials or a fragment")
    if not is_local_path(absolute.path):
        raise ValueError("redirect path is not a safe local path")

    expected_mount = normalize_mount_path(mount)
    if not expected_mount or not (
        absolute.path == expected_mount or absolute.path.startswith(expected_mount + "/")
    ):
        raise ValueError("redirect escaped the expected mount")
    return urlunsplit((absolute.scheme, absolute.netloc, absolute.path, absolute.query, ""))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origin", required=True)
    parser.add_argument("--mount", required=True)
    parser.add_argument("--location", required=True)
    args = parser.parse_args()
    try:
        print(
            safe_redirect_target(
                origin=args.origin,
                mount=args.mount,
                location=args.location,
            )
        )
    except ValueError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
