#!/usr/bin/env python3
"""PERF-024: evidence path or waive ledger consistent with DECIDE-024 disposition.

* ``--allow-undecided``: empty ledger + empty evidence_path OK when disposition is
  undecided.
* ``polling_only``: every owned prior_id must have a terminal row.
* ``prove_ops``: ``evidence_path`` must exist and be non-empty relative to repo root.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
DISPOSITION = ROOT / "docs" / "acceptance" / "live-disposition-024.toml"
LEDGER = ROOT / "docs" / "acceptance" / "waive-perf-024.toml"
TERMINALS = frozenset({"waived", "superseded", "verified"})
OWNED_DEFAULT = ("PERF-10-001",)


def _load(path: Path) -> dict[str, object]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must be a TOML table")
    return data


def _rows(data: dict[str, object]) -> list[dict[str, object]]:
    raw = data.get("rows", [])
    if not isinstance(raw, list):
        raise ValueError("rows must be a list")
    out: list[dict[str, object]] = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError(f"row must be a table, got {type(item).__name__}")
        if not item:
            continue
        out.append(item)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-undecided",
        action="store_true",
        help="Allow empty evidence/ledger when disposition is undecided.",
    )
    args = parser.parse_args(argv)
    errors: list[str] = []

    for path in (DISPOSITION, LEDGER):
        if not path.is_file():
            print(f"missing {path.relative_to(ROOT)}", file=sys.stderr)
            return 1

    try:
        disp = _load(DISPOSITION)
        ledger = _load(LEDGER)
        rows = _rows(ledger)
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        return 1

    disposition = disp.get("disposition")
    if disposition not in {"undecided", "prove_ops", "polling_only"}:
        print(f"invalid disposition {disposition!r}", file=sys.stderr)
        return 1

    if ledger.get("disposition_gate") != "PERF-024":
        errors.append("waive-perf-024.toml disposition_gate must be PERF-024")

    owned = ledger.get("owned_prior_ids", list(OWNED_DEFAULT))
    if not isinstance(owned, list) or not owned:
        errors.append("owned_prior_ids must be a non-empty list")
        owned = list(OWNED_DEFAULT)

    evidence_path = ledger.get("evidence_path", "")
    if not isinstance(evidence_path, str):
        errors.append("evidence_path must be a string")
        evidence_path = ""

    if disposition == "undecided":
        if not args.allow_undecided:
            errors.append("disposition undecided; pass --allow-undecided for packet refine")
    elif disposition == "polling_only":
        by_id = {str(r.get("id")): r for r in rows if r.get("id")}
        for pid in owned:
            row = by_id.get(str(pid))
            if row is None:
                errors.append(f"polling_only missing waive row for {pid}")
                continue
            terminal = row.get("terminal")
            if terminal not in TERMINALS:
                errors.append(
                    f"{pid}: terminal must be one of {sorted(TERMINALS)}; got {terminal!r}"
                )
            note = row.get("note")
            if not isinstance(note, str) or len(note.strip()) < 12:
                errors.append(f"{pid}: note must be a non-trivial string")
            owner = row.get("owner")
            if not isinstance(owner, str) or not owner.strip():
                errors.append(f"{pid}: owner must be a non-empty string")
    elif disposition == "prove_ops":
        if not evidence_path.strip():
            errors.append("prove_ops requires non-empty evidence_path in waive-perf-024.toml")
        else:
            evidence = ROOT / evidence_path
            if not evidence.is_file():
                errors.append(f"prove_ops evidence_path missing: {evidence_path}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    print(f"ok: PERF-024 disposition={disposition!r} rows={len(rows)} evidence={evidence_path!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
