#!/usr/bin/env python3
"""Shared helpers for phase 0.33 gate checkers."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-033.toml"
RELEASE_PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_33.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0066-HEDRON-POSIT.md"
PROBE_RUNBOOK = ROOT / "docs" / "acceptance" / "CONNECT_PROBE_033.md"
PROBE_RESULT = ROOT / "docs" / "acceptance" / "realconnect-033" / "RESULT.log"
PROBE_RESULT_MINIMUM = ROOT / "docs" / "acceptance" / "realconnect-033-202506" / "RESULT.log"
FIXTURES = ROOT / "tests" / "fixtures" / "posit-connect"
REVIEW_BRIEF = ROOT / "docs" / "acceptance" / "security-review-033" / "BRIEF.md"
UPGRADE_FIXTURES = ROOT / "docs" / "acceptance" / "upgrade-fixtures-033.md"


def require_files(paths: list[Path], errors: list[str]) -> None:
    for path in paths:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")


def require_dirs(paths: list[Path], errors: list[str]) -> None:
    for path in paths:
        if not path.is_dir():
            errors.append(f"missing directory {path.relative_to(ROOT)}")


def require_inventory_packages(names: tuple[str, ...], errors: list[str]) -> None:
    if not INVENTORY.is_file():
        errors.append("missing production-grade-inventory-033.toml")
        return
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    packages = data.get("packages")
    if not isinstance(packages, list):
        errors.append("inventory missing packages list")
        return
    missing = [name for name in names if name not in packages]
    if missing:
        errors.append(f"inventory missing packages: {missing}")


def require_inventory_keys(
    package: str,
    *,
    supported: tuple[str, ...] = (),
    experimental: tuple[str, ...] = (),
    excluded: tuple[str, ...] = (),
    errors: list[str],
) -> None:
    if not INVENTORY.is_file():
        errors.append("missing production-grade-inventory-033.toml")
        return
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    section = data.get(package)
    if not isinstance(section, dict):
        errors.append(f"inventory missing [{package}]")
        return
    for label, expected in (
        ("supported", supported),
        ("experimental", experimental),
        ("excluded", excluded),
    ):
        have = set(section.get(label) or [])
        missing = [key for key in expected if key not in have]
        if missing:
            errors.append(f"{package} inventory missing {label} keys: {missing}")


def rfc_is_accepted() -> bool:
    if not RFC.is_file():
        return False
    for line in RFC.read_text(encoding="utf-8").splitlines()[:20]:
        if line.strip().lower().startswith("**status:**"):
            return "accepted" in line.lower()
    return False


def cut_matrix_has_tbd() -> bool:
    if not RELEASE_PACKET.is_file():
        return True
    text = RELEASE_PACKET.read_text(encoding="utf-8")
    # Only the Exact cut matrix section matters.
    if "## Exact cut matrix" not in text:
        return True
    section = text.split("## Exact cut matrix", 1)[1].split("## ", 1)[0]
    return "TBD" in section


def run_pytest(rel_paths: list[str], label: str) -> int:
    existing = [rel for rel in rel_paths if (ROOT / rel).exists()]
    if not existing:
        print(f"{label}: no pytest paths present (skipped)", file=sys.stderr)
        return 0
    cmd = [sys.executable, "-m", "pytest", *existing, "-q", "--tb=short"]
    print("+", *cmd)
    try:
        subprocess.check_call(cmd, cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        print(f"{label} pytest failed ({exc.returncode})", file=sys.stderr)
        return 1
    return 0


def fail_errors(errors: list[str], label: str) -> int:
    if errors:
        for item in errors:
            print(f"{label}: {item}", file=sys.stderr)
        return 1
    return 0
