#!/usr/bin/env python3
"""EXTRAS-025: extras landmine quarantine XOR for phase 0.25.

Reads ``docs/acceptance/extras-quarantine-025.toml``.

* ``--allow-undecided`` (packet refine): accept ``disposition = \"undecided\"``.
* Cut (omit flag): require ``quarantine`` or ``finish_supported`` and matching SSOT
  phrases in PRODUCTION_ARCHETYPE / What's ready / STATUS.
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISPOSITION = ROOT / "docs" / "acceptance" / "extras-quarantine-025.toml"
SSOT = ROOT / "docs" / "api" / "PRODUCTION_ARCHETYPE.md"
WHATS_READY = ROOT / "docs" / "guides" / "whats-ready.md"
STATUS = ROOT / "docs" / "STATUS.md"

ALLOWED = frozenset({"undecided", "quarantine", "finish_supported"})
REQUIRED_LANDMINES = ("CodeEditor", "TerminalView", "joystick", "device")


def _load() -> dict[str, object]:
    data = tomllib.loads(DISPOSITION.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("disposition file must be a TOML table")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-undecided",
        action="store_true",
        help="Allow disposition=undecided (packet refine / pre-cut).",
    )
    args = parser.parse_args(argv)

    errors: list[str] = []
    for path in (DISPOSITION, SSOT, WHATS_READY, STATUS):
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    try:
        data = _load()
    except Exception as exc:  # noqa: BLE001
        print(f"failed to parse {DISPOSITION}: {exc}", file=sys.stderr)
        return 1

    disposition = data.get("disposition")
    if not isinstance(disposition, str) or disposition not in ALLOWED:
        print(
            f"disposition must be one of {sorted(ALLOWED)}; got {disposition!r}",
            file=sys.stderr,
        )
        return 1

    landmines = data.get("landmines")
    if not isinstance(landmines, list):
        print("landmines must be a list", file=sys.stderr)
        return 1
    missing = [name for name in REQUIRED_LANDMINES if name not in landmines]
    if missing:
        print(f"landmines missing required entries: {missing}", file=sys.stderr)
        return 1

    if disposition == "undecided" and not args.allow_undecided:
        print(
            "disposition is undecided; pass --allow-undecided for packet refine "
            "or set quarantine / finish_supported at cut",
            file=sys.stderr,
        )
        return 1

    ssot = SSOT.read_text(encoding="utf-8")
    for needle in (
        "CodeEditor",
        "TerminalView",
        "joystick",
        "quarantine",
        "finish_supported",
        "hedron[extras]",
        "EXTRAS-025",
    ):
        if needle not in ssot:
            errors.append(f"PRODUCTION_ARCHETYPE.md missing required mention: {needle}")

    corpus = "\n".join(
        [
            ssot,
            WHATS_READY.read_text(encoding="utf-8"),
            STATUS.read_text(encoding="utf-8"),
        ]
    )

    if disposition == "quarantine":
        if "experimental" not in corpus.lower():
            errors.append("quarantine cut requires experimental labeling in SSOT corpus")
        if "hedron[extras]" not in corpus:
            errors.append("quarantine cut requires hedron[extras] honesty in SSOT corpus")

    if disposition == "finish_supported" and "Supported" not in corpus:
        errors.append("finish_supported cut requires Supported labeling in SSOT corpus")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    mode = "allow-undecided" if args.allow_undecided else "cut"
    print(f"ok: EXTRAS-025 disposition={disposition!r} ({mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
