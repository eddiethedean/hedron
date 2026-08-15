"""CLI command: watch sources and rebuild atomically."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


def _cmd_dev(args: argparse.Namespace) -> int:
    from hedron.build import run_build
    from hedron.config import load_hedron_settings

    base = Path(args.project or Path.cwd()).resolve()
    settings = load_hedron_settings(base)
    roots = list(settings.resolved_roots(base=base))
    watch_exts = {
        ".css",
        ".html",
        ".jinja",
        ".jinja2",
        ".mjs",
        ".js",
        ".png",
        ".svg",
        ".jpg",
        ".jpeg",
        ".webp",
    }
    print(f"hedron dev watching {roots or [base]} (Ctrl+C to stop)", file=sys.stderr)
    result = run_build(project_dir=base, settings=settings, production=False)
    print(f"initial build → {result.build_dir}", file=sys.stderr)
    if args.once:
        return 0

    mtimes: dict[Path, float] = {}

    def snapshot() -> dict[Path, float]:
        current: dict[Path, float] = {}
        search_roots = roots or [base]
        for root in search_roots:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if path.is_file() and path.suffix.lower() in watch_exts:
                    current[path] = path.stat().st_mtime
        return current

    mtimes = snapshot()
    try:
        while True:
            time.sleep(args.interval)
            current = snapshot()
            if current != mtimes:
                mtimes = current
                try:
                    result = run_build(project_dir=base, settings=settings, production=False)
                    print(f"rebuilt → {result.build_dir}", file=sys.stderr)
                except Exception as exc:  # noqa: BLE001
                    print(f"build failed (previous output retained): {exc}", file=sys.stderr)
    except KeyboardInterrupt:
        print("stopped", file=sys.stderr)
        return 0
