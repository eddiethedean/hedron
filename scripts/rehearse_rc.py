#!/usr/bin/env python3
"""Rehearse a published 1.0.0rcN (or local dist/) install path for phase 0.8 exit.

This does not publish. It verifies clean-install smoke against wheels in --dist-dir
(default: ./dist) or a requirement pin like hedron==1.0.0rc1 from an index.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dist-dir",
        type=Path,
        default=ROOT / "dist",
        help="Directory containing built wheels (local rehearsal)",
    )
    parser.add_argument(
        "--requirement",
        default=None,
        help="Optional pip requirement (e.g. hedron==1.0.0rc1) for index installs",
    )
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="hedron-rc-") as tmp:
        venv_dir = Path(tmp) / "venv"
        if shutil.which("uv"):
            subprocess.check_call(["uv", "venv", str(venv_dir), "--python", "3.12"])
            py = venv_dir / "bin" / "python"
            pip_cmd = ["uv", "pip", "install", "--python", str(py)]
        else:
            import venv

            venv.create(venv_dir, with_pip=True)
            py = venv_dir / ("Scripts" if sys.platform == "win32" else "bin") / "python"
            pip_cmd = [str(py), "-m", "pip", "install"]

        if args.requirement:
            subprocess.check_call([*pip_cmd, args.requirement])
        else:
            wheels = sorted(args.dist_dir.glob("*.whl"))
            if not wheels:
                print(f"no wheels in {args.dist_dir}; build packages first", file=sys.stderr)
                return 1
            # Install core first, then flagship, then adapters/extras present in dist.
            ordered: list[Path] = []
            for prefix in (
                "hedron_core-",
                "hedron-",
                "hedron_data-",
                "hedron_flask-",
                "hedron_django-",
                "hedron_charts-",
                "hedron_explorer-",
                "hedron_sample_kit-",
            ):
                ordered.extend(w for w in wheels if w.name.startswith(prefix))
            # de-dupe preserving order
            seen: set[Path] = set()
            unique = []
            for w in ordered:
                if w not in seen:
                    seen.add(w)
                    unique.append(w)
            subprocess.check_call([*pip_cmd, *[str(w) for w in unique]])

        code = (
            "from hedron_core import Page, Text, RenderMode, render\n"
            "html = render(Page(Text('rc-ok'), title='RC'), mode=RenderMode.PAGE).html\n"
            "assert 'rc-ok' in html and html.lower().startswith('<!doctype')\n"
            "from hedron import Hedron, __version__\n"
            "print('ok: rc smoke', __version__)\n"
        )
        subprocess.check_call([str(py), "-c", code])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
