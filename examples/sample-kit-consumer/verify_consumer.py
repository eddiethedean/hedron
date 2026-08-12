#!/usr/bin/env python3
"""Assert hedron-sample-kit entry-point discovery from an installed distribution."""

from __future__ import annotations

import importlib.metadata
import sys


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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
