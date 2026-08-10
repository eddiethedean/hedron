#!/usr/bin/env python3
"""Validate the phase 0.21 human AT acceptance packet (D-052).

While gates are Planned, this checker confirms protocol files, ledger schema, and the
redacted example row exist and validate. Pass ``--require-sessions`` only when flipping
SR-021 / PARTICIPANT-021 / ARTIFACT-021 / REMEDIATE-021 to Verified after real sessions.
PROTOCOL-021 never requires session evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUMAN_AT = ROOT / "docs" / "acceptance" / "human-at"
REQUIRED_FILES = (
    HUMAN_AT / "PROTOCOL.md",
    HUMAN_AT / "PRIVACY.md",
    HUMAN_AT / "task-scripts.md",
    HUMAN_AT / "ledger.schema.json",
    HUMAN_AT / "README.md",
    HUMAN_AT / "ledger" / "hat-example-0001.json",
    ROOT / "docs" / "acceptance" / "release-gate-0.21.toml",
    ROOT / "docs" / "acceptance" / "RELEASE_0_21.md",
)

GateId = str


def _load_sys_path() -> None:
    core_src = ROOT / "packages" / "hedron-core" / "src"
    if str(core_src) not in sys.path:
        sys.path.insert(0, str(core_src))


def check_protocol_files() -> list[str]:
    errors: list[str] = []
    for path in REQUIRED_FILES:
        if not path.is_file():
            errors.append(f"missing required packet file: {path.relative_to(ROOT)}")
    return errors


def _parse_ledger_rows() -> tuple[list[object], list[str]]:
    _load_sys_path()
    from hedron_core.a11y import HumanAtRecord

    errors: list[str] = []
    schema_path = HUMAN_AT / "ledger.schema.json"
    if not schema_path.is_file():
        return [], [f"missing schema: {schema_path.relative_to(ROOT)}"]
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [], [f"invalid ledger.schema.json: {exc}"]
    if schema.get("title") != "Hedron human AT redacted ledger row":
        errors.append("ledger.schema.json title mismatch")

    ledger_dir = HUMAN_AT / "ledger"
    rows = sorted(ledger_dir.glob("*.json")) if ledger_dir.is_dir() else []
    if not rows:
        errors.append("no ledger/*.json rows found")
        return [], errors

    parsed: list[HumanAtRecord] = []
    for row_path in rows:
        try:
            data = json.loads(row_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{row_path.name}: invalid JSON ({exc})")
            continue
        try:
            parsed.append(HumanAtRecord.from_dict(data))
        except (ValueError, TypeError) as exc:
            errors.append(f"{row_path.name}: {exc}")
    return parsed, errors  # type: ignore[return-value]


def check_ledger_rows(
    *,
    require_session_evidence: bool,
    gate: GateId | None = None,
) -> list[str]:
    parsed, errors = _parse_ledger_rows()
    if errors and not parsed:
        return errors

    if not require_session_evidence:
        return errors

    # PROTOCOL never requires session floors even if --require-sessions is passed alone.
    if gate == "PROTOCOL-021":
        return errors

    real = [r for r in parsed if getattr(r, "result", None) != "placeholder"]
    if not real:
        errors.append(
            "Verified gates require non-placeholder ledger rows "
            "(run human AT sessions per PROTOCOL.md)"
        )
        return errors

    need_sr = gate in (None, "SR-021")
    need_participant = gate in (None, "PARTICIPANT-021")
    need_artifact = gate in (None, "ARTIFACT-021")
    need_remediate = gate in (None, "REMEDIATE-021")

    if need_sr:
        combos = {r.combo_id for r in real if not r.stretch}  # type: ignore[attr-defined]
        for needed in (
            "vo-safari-macos",
            "nvda-firefox-windows",
            "talkback-chromium-android",
        ):
            if needed not in combos:
                errors.append(f"SR-021 missing Verified combo evidence: {needed}")

    if need_participant:
        categories = {
            r.participant_category  # type: ignore[attr-defined]
            for r in real
            if r.participant_category and r.participant_category != "maintainer_sr"  # type: ignore[attr-defined]
        }
        sessions = {r.session_id for r in real if r.session_id}  # type: ignore[attr-defined]
        if len(sessions) < 2:
            errors.append("PARTICIPANT-021 requires ≥2 distinct session_id values")
        if "screen_reader" not in categories:
            errors.append("PARTICIPANT-021 requires a screen_reader participant_category")
        if not categories.intersection({"motor", "low_vision", "cognitive"}):
            errors.append(
                "PARTICIPANT-021 requires motor, low_vision, or cognitive participant_category"
            )

    if need_artifact:
        for row in real:
            if (
                not str(getattr(row, "known_issue", "") or "").strip()
                and not getattr(row, "issue_url", None)
                and (
                    getattr(row, "severity", "none") != "none"
                    or getattr(row, "result", "") in {"fail", "blocker"}
                )
            ):
                # Fail/blocker session rows still need a known_issue note or linked issue for
                # ARTIFACT-021 inventory completeness (even when severity is none).
                errors.append(
                    f"ARTIFACT-021 {row.record_id}: fail/blocker rows need "  # type: ignore[attr-defined]
                    "known_issue or issue_url"
                )
            notes = str(getattr(row, "notes", "") or "")
            if "placeholder" in notes.lower() and getattr(row, "result", "") != "placeholder":
                errors.append(
                    f"ARTIFACT-021 {row.record_id}: notes still describe placeholder evidence"  # type: ignore[attr-defined]
                )

    if need_remediate:
        blockers = [r for r in real if getattr(r, "result", "") == "blocker"]
        for row in blockers:
            if not getattr(row, "waiver_id", None) and not getattr(row, "issue_url", None):
                errors.append(
                    f"REMEDIATE-021 {row.record_id}: blocker requires waiver_id or issue_url"  # type: ignore[attr-defined]
                )
        # Soft floor: when requiring sessions, at least one real row must acknowledge
        # remediation ownership via owner + retest_date (already validated on parse).
        if not any(getattr(r, "owner", "").strip() for r in real):
            errors.append("REMEDIATE-021 requires owner on non-placeholder rows")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--gate",
        choices=[
            "PROTOCOL-021",
            "SR-021",
            "PARTICIPANT-021",
            "ARTIFACT-021",
            "REMEDIATE-021",
            "PKG-021",
        ],
        help="Optional gate id (default: full packet check)",
    )
    parser.add_argument(
        "--require-sessions",
        action="store_true",
        help="Fail unless non-placeholder session ledger rows meet Verified floors",
    )
    args = parser.parse_args(argv)

    errors = check_protocol_files()
    if args.gate == "PKG-021":
        # Packaging evidence is scripts/verify_pkg_21.py; packet files still required.
        pass
    else:
        require = bool(args.require_sessions) and args.gate != "PROTOCOL-021"
        errors.extend(
            check_ledger_rows(
                require_session_evidence=require,
                gate=args.gate,
            )
        )

    seen: set[str] = set()
    unique: list[str] = []
    for err in errors:
        if err not in seen:
            seen.add(err)
            unique.append(err)

    if unique:
        for err in unique:
            print(f"error: {err}", file=sys.stderr)
        return 1
    label = args.gate or "packet"
    print(f"ok: human AT {label} ({HUMAN_AT.relative_to(ROOT)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
