#!/usr/bin/env python3
"""Probe the live Workbench-mounted WebSocket used by REALWB-029."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from websockets.asyncio.client import connect


async def _probe_once(url: str, expected: str, authorization_key_file: str | None) -> None:
    headers = None
    if authorization_key_file:
        key = (
            await asyncio.to_thread(
                Path(authorization_key_file).read_text,
                encoding="utf-8",
            )
        ).strip()
        if not key:
            raise RuntimeError("authorization key file was empty")
        headers = {"Authorization": f"Key {key}"}
    async with connect(
        url,
        additional_headers=headers,
        open_timeout=5,
        close_timeout=5,
    ) as socket:
        message = await asyncio.wait_for(socket.recv(), timeout=5)
    if message != expected:
        raise RuntimeError(f"unexpected WebSocket message: {message!r}")


async def _probe(
    url: str, expected: str, authorization_key_file: str | None, attempts: int
) -> None:
    """Retry a newly-started ASGI listener without hiding a persistent failure."""
    failure: Exception | None = None
    for attempt in range(attempts):
        try:
            await _probe_once(url, expected, authorization_key_file)
            return
        except Exception as exc:  # noqa: BLE001  # readiness can race connection setup
            failure = exc
            if attempt + 1 < attempts:
                await asyncio.sleep(0.5)
    assert failure is not None
    raise RuntimeError(f"WebSocket probe failed after {attempts} attempts: {failure}") from failure


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--expected", default="native-ws")
    parser.add_argument("--authorization-key-file")
    parser.add_argument("--attempts", type=int, default=3)
    args = parser.parse_args()
    if args.attempts < 1 or args.attempts > 10:
        parser.error("--attempts must be between 1 and 10")
    asyncio.run(_probe(args.url, args.expected, args.authorization_key_file, args.attempts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
