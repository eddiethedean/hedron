#!/usr/bin/env python3
"""DECIDE-024: live-disposition XOR + SSOT label agreement for phase 0.24.

Reads ``docs/acceptance/live-disposition-024.toml``.

* ``--allow-undecided`` (packet refine): accept ``disposition = \"undecided\"``.
* Cut (omit flag): require ``prove_ops`` or ``polling_only`` and matching phrases
  across LIVE_DISPOSITION / STABILITY / What's ready / STATUS.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
DISPOSITION = ROOT / "docs" / "acceptance" / "live-disposition-024.toml"
LIVE_DOC = ROOT / "docs" / "api" / "LIVE_DISPOSITION.md"
STABILITY = ROOT / "docs" / "api" / "STABILITY.md"
WHATS_READY = ROOT / "docs" / "guides" / "whats-ready.md"
STATUS = ROOT / "docs" / "STATUS.md"

ALLOWED = frozenset({"undecided", "prove_ops", "polling_only"})
REQUIRED_PRIOR = ("BROWSER-10-001", "PERF-10-001", "LIVE-011-BROWSER")

# Additional phrases required when disposition is prove_ops (cut path A).
PROVE_OPS_PHRASES = (
    "prove_ops",
    "Supported-with-ops",
)


def _load() -> dict[str, object]:
    data = tomllib.loads(DISPOSITION.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("disposition file must be a TOML table")
    return data


def _require_files() -> list[str]:
    errors: list[str] = []
    for path in (DISPOSITION, LIVE_DOC, STABILITY, WHATS_READY, STATUS):
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-undecided",
        action="store_true",
        help="Allow disposition=undecided (packet refine / pre-cut).",
    )
    args = parser.parse_args(argv)

    errors = _require_files()
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

    prior = data.get("prior_ids")
    if not isinstance(prior, list):
        print("prior_ids must be a list", file=sys.stderr)
        return 1
    missing_prior = [pid for pid in REQUIRED_PRIOR if pid not in prior]
    if missing_prior:
        print(f"prior_ids missing required IDs: {missing_prior}", file=sys.stderr)
        return 1

    fallback = data.get("supported_production_fallback")
    if fallback != "polling":
        print(
            f"supported_production_fallback must be 'polling'; got {fallback!r}",
            file=sys.stderr,
        )
        return 1

    if disposition == "undecided" and not args.allow_undecided:
        print(
            "disposition is undecided; pass --allow-undecided for packet refine "
            "or set prove_ops / polling_only at cut",
            file=sys.stderr,
        )
        return 1

    live_text = LIVE_DOC.read_text(encoding="utf-8")
    for needle in (
        "prove_ops",
        "polling_only",
        "EXPLORER-10-001",
        "BROWSER-10-001",
        "PERF-10-001",
        "LIVE-011-BROWSER",
        "job_status_sse_response",
    ):
        if needle not in live_text:
            errors.append(f"LIVE_DISPOSITION.md missing required mention: {needle}")

    corpus = "\n".join(
        [
            live_text,
            STABILITY.read_text(encoding="utf-8"),
            WHATS_READY.read_text(encoding="utf-8"),
            STATUS.read_text(encoding="utf-8"),
        ]
    )

    if disposition in {"undecided", "polling_only"}:
        # Must still prefer polling / call live experimental somewhere in SSOT set.
        if not any(p in corpus for p in ("Prefer polling", "prefer polling", "polling")):
            errors.append("SSOT corpus missing polling fallback guidance")
        if "experimental" not in corpus.lower():
            errors.append("SSOT corpus missing experimental live labeling")
        # Must not claim SSE/WS unqualified Supported in LIVE_DISPOSITION while B/undecided.
        forbidden = (
            "SSE observation is **Supported**",
            "Official HTMX SSE is Supported",
            "FastAPI SSE helpers are Supported",
        )
        for phrase in forbidden:
            if phrase in live_text:
                errors.append(
                    f"LIVE_DISPOSITION must not claim Supported live under "
                    f"{disposition}: {phrase!r}"
                )

    if disposition == "prove_ops":
        for phrase in PROVE_OPS_PHRASES:
            if phrase not in corpus:
                errors.append(
                    f"prove_ops cut requires SSOT phrase {phrase!r} across "
                    "LIVE_DISPOSITION / STABILITY / What's ready / STATUS"
                )

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    mode = "allow-undecided" if args.allow_undecided else "cut"
    print(f"ok: DECIDE-024 disposition={disposition!r} ({mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
