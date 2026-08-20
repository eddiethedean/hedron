#!/usr/bin/env python3
"""Assert hedron-sample-kit entry-point discovery from an installed distribution."""

from __future__ import annotations

import importlib.metadata
import sys
from pathlib import Path


def main() -> int:
    eps = importlib.metadata.entry_points()
    selected = (
        eps.select(group="hedron.plugins")
        if hasattr(eps, "select")
        else eps.get("hedron.plugins", [])  # type: ignore[attr-defined]
    )
    names = sorted({ep.name for ep in selected})
    if "sample_kit" not in names:
        print(f"PLUGIN-031: sample_kit entry point missing; found={names}", file=sys.stderr)
        return 1
    ep = next(ep for ep in selected if ep.name == "sample_kit")
    register = ep.load()
    from hedron_core.plugins import PluginContext
    from hedron_sample_kit.plugin import PLUGIN_META

    ctx = PluginContext(PLUGIN_META)
    register(ctx)
    from hedron_sample_kit.components.Callout import Callout

    assert Callout(message="plugin-ok").props.message == "plugin-ok"
    print("ok: sample_kit entry point loaded and Callout works")

    from hedron_sample_kit import list_variants

    print(f"ok: SAMPLE-054 variants present: {', '.join(list_variants()) or '(none)'}")

    source = Path(__file__).resolve().parents[2] / "packages" / "hedron-sample-kit"
    try:
        from hedron.package_doctor import diagnose_package
    except ImportError:
        print("skip: DOCTOR-054 needs the hedron distribution installed")
        return 0
    if not (source / "pyproject.toml").is_file():
        print("skip: DOCTOR-054 needs the package source tree")
        return 0
    report = diagnose_package(source)
    if not report["ok"]:
        print(f"DOCTOR-054: package doctor failed: {report['diagnostics']}", file=sys.stderr)
        return 1
    print("ok: hedron package doctor reports package_doctor=True ok=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
