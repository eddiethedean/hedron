#!/usr/bin/env python3
"""Capture all documentation/README screenshots from the current runnable apps.

Run with ``uv run python scripts/generate_docs_screenshots.py`` after installing
Chromium with ``uv run playwright install chromium``. Each app runs in an isolated
local process; no published app or production data is used.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import tempfile
import time
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/assets"


@dataclass(frozen=True)
class Screenshot:
    filename: str
    app_dir: str
    module: str
    width: int
    height: int
    ready_text: str


SCREENSHOTS = (
    Screenshot("hedron-showcase.jpg", "examples/showcase", "app", 1440, 1080, "Workspace overview"),
    Screenshot("edron-showcase.jpg", "examples/edron-showcase", "app", 1440, 900, "Command center"),
    Screenshot(
        "hello-refresh.jpg",
        "docs/demos/runnable",
        "hello-refresh",
        1200,
        799,
        "Hello from hedron new",
    ),
    Screenshot("notes-form.jpg", "docs/demos/runnable", "minimal-form", 960, 720, "Leave a note"),
)


@contextmanager
def serve(screenshot: Screenshot) -> Generator[str, None, None]:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    environment = os.environ.copy()
    environment.pop("HEDRON_ACCENT", None)
    with tempfile.TemporaryFile(mode="w+") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                f"{screenshot.module}:app",
                "--app-dir",
                str(ROOT / screenshot.app_dir),
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--log-level",
                "warning",
            ],
            cwd=ROOT,
            env=environment,
            stdout=log,
            stderr=log,
        )
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline and process.poll() is None:
                with socket.socket() as sock:
                    if sock.connect_ex(("127.0.0.1", port)) == 0:
                        break
                time.sleep(0.1)
            else:
                log.seek(0)
                raise RuntimeError(f"{screenshot.filename}: app failed to start\n{log.read()}")
            yield f"http://127.0.0.1:{port}/"
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            for screenshot in SCREENSHOTS:
                with serve(screenshot) as url:
                    context = browser.new_context(
                        viewport={"width": screenshot.width, "height": screenshot.height},
                        device_scale_factor=1,
                        color_scheme="light",
                        reduced_motion="reduce",
                        locale="en-US",
                        timezone_id="UTC",
                    )
                    try:
                        page = context.new_page()
                        errors: list[str] = []
                        page.on(
                            "pageerror",
                            lambda error, collected=errors: collected.append(str(error)),
                        )
                        response = page.goto(url, wait_until="networkidle")
                        if response is None or response.status != 200:
                            raise RuntimeError(f"{screenshot.filename}: page did not return 200")
                        page.get_by_text(screenshot.ready_text, exact=True).wait_for()
                        page.evaluate("document.fonts.ready")
                        if errors:
                            raise RuntimeError(f"{screenshot.filename}: browser errors: {errors}")
                        page.screenshot(
                            path=str(OUTPUT / screenshot.filename),
                            type="jpeg",
                            quality=90,
                            full_page=True,
                            animations="disabled",
                        )
                        print(f"wrote docs/assets/{screenshot.filename}")
                    finally:
                        context.close()
        finally:
            browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
