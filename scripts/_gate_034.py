#!/usr/bin/env python3
"""Shared helpers for phase 0.34 gate checkers."""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-034.toml"
RELEASE_PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_34.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0067-PRODUCTION-GRADE-GRADIO.md"
PROBE_RUNBOOK = ROOT / "docs" / "acceptance" / "GRADIO_PROBE_034.md"
FIXTURES = ROOT / "tests" / "fixtures" / "gradio"
REVIEW_BRIEF = ROOT / "docs" / "acceptance" / "security-review-034" / "BRIEF.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "HEDRON_GRADIO_034.md"


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
        errors.append("missing production-grade-inventory-034.toml")
        return
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    packages = data.get("packages")
    if not isinstance(packages, list):
        errors.append("inventory missing packages list")
        return
    missing = [name for name in names if name not in packages]
    if missing:
        errors.append(f"inventory missing packages: {missing}")


def rfc_is_accepted(*, allow_draft: bool = False) -> bool:
    if not RFC.is_file():
        return False
    for line in RFC.read_text(encoding="utf-8").splitlines()[:20]:
        if line.strip().lower().startswith("**status:**"):
            lowered = line.lower()
            if "accepted" in lowered:
                return True
            if allow_draft and "draft" in lowered:
                return True
    return False


def cut_matrix_has_tbd() -> bool:
    if not RELEASE_PACKET.is_file():
        return True
    text = RELEASE_PACKET.read_text(encoding="utf-8")
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
